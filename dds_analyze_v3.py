import argparse
import xml.etree.ElementTree as ET
import pandas as pd



def parse_participant(participant_data, domain_id):

    participant_name = None
    participant_key = None
    property_name = None
    property_value = None
    hostname = None
    filepath = None

    for child in participant_data:

        if child.tag == "key":
            participant_key = child.find("value").text

        if child.tag == "participant_name":
            if child.find("name") is not None:
                participant_name = child.find("name").text

        if child.tag == "property":
            for element in child.iter("element"):
                if element.find("name") is not None:
                    property_name = element.find("name").text

                if element.find("value") is not None:
                    property_value = element.find("value").text

                if property_name == "dds.sys_info.hostname":
                    hostname = property_value

                if property_name == "dds.sys_info.executable_filepath":
                    filepath = property_value

            if child.find("name") is not None:
                participant_name = child.find("name").text

        if child.tag == "default_unicast_locators":
            for element in child.iter("element"):
                if element.find("address") is not None:
                    address = element.find("address").text
                    ip_list = address.split(",")
                    last_4_ip_list = ip_list[-4:]

                if element.find("kind") is not None:
                    kind = element.find("kind").text
                    # If UDP Locator
                    if kind == "1":
                        ip_bytes = [int(hex_val, 16) for hex_val in last_4_ip_list]
                        ip_str = ".".join(map(str, ip_bytes))
                        break

    participant = [domain_id, participant_name, participant_key, ip_str, hostname, filepath]

    return participant


def parse_endpoint(data_element, kind, participant_key, domain_id):

    topic_name = None
    type_name = None
    reliable = None
    deadline = None
    content_filter = None
    multicast = None
    multicast_ip_str = None
    max_sample_serialized_size = ""
    
    for child in data_element:
        if child.tag == "topic_name":
            topic_name = child.text
        elif child.tag == "type_name":
            type_name = child.text
        elif child.tag == "max_sample_serialized_size":
            max_sample_serialized_size = child.text
        elif child.tag == "reliability":
            reliable = child.find("kind").text
        elif child.tag == "deadline":
            sec = child.find("period/sec").text
            nanosec = child.find("period/nanosec").text
            if (sec == "DURATION_INFINITE_SEC" or nanosec == "DURATION_INFINITE_NSEC"):
                deadline = ""
            else:
                deadline = int(sec) + int(nanosec) / 1000000000
        elif child.tag == "content_filter_property":
            if child.find("filter_expression") is not None:
                content_filter = child.find("filter_expression").text
        elif child.tag == "multicast_locators":
            for element in child.iter("element"):
                if element.find("address") is not None:
                    multicast = element.find("address").text
                    ip_list = multicast.split(",")
                    last_4_ip_list = ip_list[-4:]
                    ip_bytes = [int(hex_val, 16) for hex_val in last_4_ip_list]
                    multicast_ip_str = ".".join(map(str, ip_bytes))

    endpoint = [domain_id, kind, topic_name, type_name, participant_key, reliable, max_sample_serialized_size, deadline, content_filter, multicast_ip_str]

    return endpoint
        

def test_excess_endpoints(endpoints_df, domain_id):

  # Split up by readers/writers
  group_by_kind = {name: group for name, group in endpoints_df.groupby('kind')}

  writers_no_readers = group_by_kind["writer"].merge(group_by_kind["reader"], how='outer', on='topic_name', indicator='ind').query(
      'ind == "left_only"')
  writers_no_readers.to_csv(f"./writers_no_readers_{domain_id}.csv")

  readers_no_writers = group_by_kind["reader"].merge(group_by_kind["writer"], how='outer', on='topic_name', indicator='ind').query(
      'ind == "left_only"')
  
  readers_no_writers.to_csv(f"./readers_no_writers_domain_{domain_id}.csv")


def test_inconsistent_type_names(endpoints_df, domain_id):

  inconsistent_types_list = []
  for name, group in endpoints_df.groupby('topic_name'):
      if len(group['type_name'].unique()) != 1:
          inconsistent_types_list.append(group)
  
  inconsistent_types_df = pd.concat(inconsistent_types_list, ignore_index=True)
  inconsistent_types_df.to_csv(f"./inconsistent_types_domain_{domain_id}.csv")


def test_potential_multicast_readers(endpoints_df, domain_id):

  multicast_readers_list  = []

  for name, group in endpoints_df.groupby(['topic_name', 'kind']):
      if name[1] == "reader":
        if group["content_filter"].isnull().all():
            if len(group) > 2:
              multicast_readers_list.append(group)

  multicast_readers_df = pd.concat(multicast_readers_list, ignore_index=True)
  multicast_readers_df.to_csv(f"./potential_multicast_readers_domain_{domain_id}.csv")


def test_reliable_writer_besteffort_readers(endpoints_df, domain_id):

  mismatch_reliable_list = []
  for name, group in endpoints_df.groupby(['topic_name']):
  
    found = False
    # if name[1] == "reader":
    for index, row in group.iterrows():
      if row["reliable"] == "RELIABLE_RELIABILITY_QOS" and row["kind"] == "writer":
        found = True
      
      if row["reliable"] == "BEST_EFFORT_RELIABILITY_QOS" and row["kind"] == "reader":
        if found:
          # print("Reliability mismatch")
          mismatch_reliable_list.append(group)

  mismatch_reliable_df = pd.concat(mismatch_reliable_list, ignore_index=True)
  mismatch_reliable_df.to_csv(f"./mismatch_reliable_domain_{domain_id}.csv")


def get_devices(participants_df, devices_df):

  for name, group in participants_df.groupby("device_ip"):
    first_row = group.iloc[0]
    new_row = {
        "device_ip": name,
        "device_name": first_row["device_name"]
    }

  devices_df = pd.concat([devices_df, pd.DataFrame([new_row])], ignore_index=True)
  devices_df.to_csv("./all_devices.csv")
  

def ProcessFile(filename, participants_df, endpoints_df):

    # Set up Parser
    tree = ET.parse(filename)
    root = tree.getroot()

    # Domain Participants
    domain_participants = root.findall(".//domain_participants/value/element")

    for domain_participant in domain_participants:
        
        domain_id = domain_participant.find("domain_id").text
            
        participant_data = domain_participant.find("participant_data")
        participant = parse_participant(participant_data, domain_id)

        participants_df.loc[len(participants_df)] = participant
        
        publications = domain_participant.findall(".//publication_data")
        for publication_data in publications:
            publication = parse_endpoint(publication_data, "writer", participant[1], domain_id)
            endpoints_df.loc[len(endpoints_df)] = publication
    
        subscriptions = domain_participant.findall(".//subscription_data")
        for subscription_data in subscriptions:
            subscription = parse_endpoint(subscription_data, "reader", participant[1], domain_id)
            endpoints_df.loc[len(endpoints_df)] = subscription


  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file.")
    parser.add_argument("filename", help="Path to the file")
    args = parser.parse_args()
    filename = args.filename

    # Set up Data Frames
    devices_df = pd.DataFrame(columns=['device_ip', 'device_name'])

    participants_df = pd.DataFrame(columns=['domain_id', 'name', 'key', 'device_ip', 'device_name', 'path'])

    endpoints_df = pd.DataFrame(columns=['domain_id', 'kind', 'topic_name', 'type_name', 'participant_key', 'reliable',
                                      'max_sample_serialized_size', 'deadline', 'content_filter', 'multicast_ip_str'])

    try:
      ProcessFile(filename, participants_df, endpoints_df)
    except FileNotFoundError:
      print(f"Error: File '{filename}' not found.")

    # Get Devices
    get_devices(participants_df, devices_df)

    # Export Participants
    for name, group in participants_df.groupby('domain_id'):
      group.to_csv(f"./participants_domain_{name}.csv")

    # Run Tests
    for name, group in endpoints_df.groupby('domain_id'):
      test_excess_endpoints(group, name)
      test_inconsistent_type_names(group, name)
      test_potential_multicast_readers(group, name)
      test_reliable_writer_besteffort_readers(group, name)

    print(f"Participants QTY: {len(participants_df)}")
    print(f"Endpoints QTY: {len(endpoints_df)}")



