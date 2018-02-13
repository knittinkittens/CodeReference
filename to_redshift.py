import gzip
from functools import wraps
import boto3
from pandas import DataFrame
import codecs
import random
import string
from io import  BytesIO

def monkeypatch_method(cls):
    """
    Creates a decoration for monkey-patching a class
    Recipe from: https://mail.python.org/pipermail/python-dev/2008-January/076194.html
    Args:
        cls:
    Returns:
    """
    @wraps(cls)
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

def resolve_qualname(table_name, schema=None):
    name = '.'.join([schema, table_name]) if schema is not None else table_name
    return name
        
@monkeypatch_method(DataFrame)
def to_redshift(self, table_name, engine, s3_bucket, aws_access_key_id, aws_secret_access_key, region, how = 'append', keys = None):
    """
    Inserts dataframe to Redshift by creating a file in S3
    Args:
        self: Panda's dataframe to insert into Redshift
        table_name: Name of the table to insert dataframe
        engine: An SQL alchemy engine object
        bucket: S3 bucket name
        aws_access_key_id: from config file
        aws_secret_access_key: from config file
        how: how the dataframe should be inserted to the table
        keys: (optional) columns to upsert records on
    Returns:
        success: boolean indicating if successful
    """
    
    if how not in ['append', 'upsert', 'replace']:
        raise Exception('Unknown value to "how" parameter.')
    if how == 'upsert' and keys is None:
        raise Exception('Upsert specified, but no keys specified.')
    if how != 'upsert' and keys is not None:
        raise Exception('Upsert not specified, but keys specified.')
    if not (str == type(table_name) == type(s3_bucket) == type(aws_access_key_id) == type(aws_secret_access_key)):
        raise TypeError('Incorrect argument type')

    s3_keypath = ''.join([random.choice(string.ascii_letters) for n in range(32)])
    rand_tbl = ''.join([random.choice(string.ascii_letters) for n in range(32)])
    column_mapping = ", ".join(list(self.columns.values))

    if keys is not None and how == 'upsert': 
        key_cond = ' and '.join([rand_tbl + "." + i + "=" + table_name + "." + i for i in keys])   
        stmt = ('''create temp table {stgTbl} (like {tblName} including defaults);
				copy {stgTbl}  ({cols}) from 's3://{bkt}/{flnme}' region '{rgn}' gzip ignoreheader 1 DELIMITER as ',' COMPUPDATE FALSE EMPTYASNULL
				credentials 'aws_access_key_id={access};aws_secret_access_key={secret}';
            delete from {tblTbl} using {stgTble} where {keyCon};
				insert into {tblName} ({cols}) select {cols} from {stgTbl};
				drop table {stgTbl};
			'''.format(stgTbl 	= rand_tbl,
						tblName = table_name,
						bkt 	= s3_bucket, 
						flnme 	= s3_keypath,
						rgn 	= region,
						access	= aws_access_key_id,
						secret 	= aws_secret_access_key,
						cols 	= column_mapping,
						keyCon 	= key_cond
						)
        )
    elif how == 'append':
        # Copy rom s3 to rs
        stmt = ('''create temp table {stgTbl} (like {tblName} including defaults);
    				copy {stgTbl}  ({cols}) from 's3://{bkt}/{flnme}' region '{rgn}' gzip ignoreheader 1 DELIMITER as ',' COMPUPDATE FALSE EMPTYASNULL
    				credentials 'aws_access_key_id={access};aws_secret_access_key={secret}';
    				insert into {tblName} ({cols}) select {cols} from {stgTbl};
    				drop table {stgTbl};
    			'''.format(stgTbl 	= rand_tbl,
    						tblName = table_name,
    						bkt 	= s3_bucket, 
    						flnme 	= s3_keypath,
    						rgn 	= region,
    						access	= aws_access_key_id,
    						secret 	= aws_secret_access_key,
    						cols 	= column_mapping
    						)
                )
    elif how == 'replace':
        # Copy rom s3 to rs
        stmt = ('''create temp table {stgTbl} (like {tblName} including defaults);
    				copy {stgTbl}  ({cols}) from 's3://{bkt}/{flnme}' region '{rgn}' gzip ignoreheader 1 DELIMITER as ',' COMPUPDATE FALSE EMPTYASNULL
    				credentials 'aws_access_key_id={access};aws_secret_access_key={secret}';
                    delete from {tblName};
    				insert into {tblName} ({cols}) select {cols} from {stgTbl};
    				drop table {stgTbl};
    			'''.format(stgTbl 	= rand_tbl,
    						tblName = table_name,
    						bkt 	= s3_bucket, 
    						flnme 	= s3_keypath,
    						rgn 	= region,
    						access	= aws_access_key_id,
    						secret 	= aws_secret_access_key,
    						cols 	= column_mapping
    						)
                )
        
    try:
        print("Uploading to s3...")
        file_uploaded = self.to_s3(bucket=s3_bucket, keypath=s3_keypath, index=False, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, compress=True)
        print("Querying Redshift...")
        with engine.begin() as con:
            con.execute(stmt)
            con.execute('COMMIT;')
        print('Success...')
        success = True
    except Exception as e:
        print('Error.  Rolling back!')
        print(e)
        with engine.begin() as con:
            con.execute('ROLLBACK;')
        success = False
    finally:
        print("Deleting temp file...")
        client = boto3.client('s3')
        client.delete_object(Bucket=s3_bucket, Key=file_uploaded)
        return(success)
        
@monkeypatch_method(DataFrame)
def to_s3(self, bucket, keypath, index=False, compress=True, encoding="ascii", aws_access_key_id=None, aws_secret_access_key=None):
    """
    Writes the data frame to S3
    Args:
        self: Dataframe to upload
        bucket: S3' bucket
        keypath: S3's keypath
        index: whether to include the index of the dataframe
        compress: whether to compress the data before uploading it
        encoding: Ascii by default
        aws_access_key_id: from ~./boto by default
        aws_secret_access_key: from ~./boto by default
    Returns: The S3 URL of the file, and the credentials used to upload it
    """
    print("Exporting to S3...")
    # Figure out paths:
    keypath = "{filename}.{ext}".format(filename=keypath, ext="gzip" if compress else "csv")
    url = bucket + '/' + keypath

    # Create S3 session
    session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    aws_access_key_id     = session.get_credentials().access_key
    aws_secret_access_key = session.get_credentials().secret_key

    s3 = session.resource('s3')
    obj = s3.Object(bucket_name=bucket, key=keypath)

    # Create a memory file that allows unicode:
    buffer = BytesIO()
    codecinfo = codecs.lookup("utf8")
    fp = codecs.StreamReaderWriter(buffer, codecinfo.streamreader, codecinfo.streamwriter)

    # Compress
    gzfp = BytesIO()
    self.to_csv(fp, index=index, encoding=encoding)
    if compress:
        print("Compressing")
        fp.seek(0)
        gzipped = gzip.GzipFile(fileobj=gzfp, mode='w')
        gzipped.write(bytes(fp.read(), 'utf8'))
        gzipped.close()
        gzfp.seek(0)
    else:
        gzfp = fp
        gzfp.seek(0)

    print("Uploading to {}".format(url))

    obj.upload_fileobj(gzfp)

    return keypath
