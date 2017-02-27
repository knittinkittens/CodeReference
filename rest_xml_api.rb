#################
# Package imports
#################

require 'rest_client'
require 'nokogiri'
require 'CSV'
require 'json'

#######################
# Parameter definitions
#######################

def make_request(tracking)
	xml = "XML Request"
	url = 'URL'
	response = RestClient.post url, xml, {:content_type => :xml}
	return response
end

################################
# Create XML object for response
################################

def parse_response(response)
	stuff  = Nokogiri::XML(response)

	a = Array.new
	b = Array.new
	c = Array.new

	stuff.xpath("//xpath1//xpath2//xpath3").each do |node|
		  aa = stuff.xpath('//value')
		  a.push(aa.inner_text)
	end

	stuff.xpath("//xpath1//xpath2//xpath3a").each do |node|
		  bb = node.inner_text
		  bb.gsub("T", " ")
		  b.push(bb)
	end

	puts "parsed"


	i = 0
	b.each do |element|
		c.push(b[i] + "!")
		i = i + 1
	end

	a1 = a.zip(b).map(&:flatten)
	a2 = a1.zip(c).map(&:flatten)
	return a2
end


def main()
	arr_of_arrs = CSV.read(location, :row_sep => "\r\n")
	main_events = Array.new
	arr_of_arrs.each do |element|
		if (element[1] == "something") || (element[1] == "something else")
			begin
				param = element[0]
				response = make_request(param)
				result_array = parse_response(response)
				result_array.each do |element|
					main_results.push(element)
				end
			rescue
				param = element[0]
				error_array = [param, "NULL", "NULL", "NULL"]
				main_results.push(error_array)
			end
		end
	end
	CSV.open("outpath", "w") do |csv|
		main_results.each do |element|
			csv << element
		end
	end
end

config_file = File.open(File.dirname(__FILE__) + "/config.json", "r")
config = JSON.parse(config_file)
location = config['location']
out_location = config['out_location']
UserID  = config['UserID']
Password = config['Password']


main()