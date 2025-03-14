import rti.connextdds as dds
from rti.connextdds import PublicationBuiltinTopicData, SubscriptionBuiltinTopicData
import threading
import time
import csv

# Global map to store types
entities = {}
participants = {}
edges = {}


class Entity:
  def __init__(self, id=None, topic_name=None, type_name=None, kind=None, p_ip=None, p_name=None, p_guid=None):
      self.id = id,
      self.topic_name = topic_name
      self.type_name = type_name
      self.kind = kind
      self.p_ip = p_ip
      self.p_name = p_name
      self.p_guid = p_guid

class Participant:
    def __init__(self, name=None, ip=None):
        self.name = name
        self.ip = ip

class Edge:
    def __init__(self, source=None, target=None, topic_name=None):
        self.source = source
        self.target = target
        self.topic_name = topic_name


# Listener for publication discovery
class PublicationListener(dds.PublicationBuiltinTopicData.DataReaderListener):

    def __init__(self):
        super(PublicationListener, self).__init__()

    def on_data_available(self, reader):

        for data, info in reader.take():
            if info.valid:
                # print(f"Discovered Writer {data.topic_name}")
                key_list = data.key.value
                key_int = int(''.join(map(str, key_list)))
                # print(f"Writer Key: {key_int}")
                type_name = data.type_name
                topic_name = data.topic_name

                p_guid_list = data.participant_key.value
                p_guid_int = int(''.join(map(str, p_guid_list)))

                writer = Entity(topic_name=topic_name,type_name=type_name, kind="Writer", p_guid=p_guid_int)

                if key_int not in entities:
                    print(f"Adding Writer to list: {writer.topic_name}")
                    entities[key_int] = writer

# Listener for subscription discovery
class SubscriptionListener(dds.SubscriptionBuiltinTopicData.DataReaderListener):
    def on_data_available(self, reader):

        for data, info in reader.take():
            if info.valid:
                # print(f"Discovered Reader {data.topic_name}")
                key_list = data.key.value
                key_int = int(''.join(map(str, key_list)))
                # print(f"Reader Key: {key_int}")
                type_name = data.type_name
                topic_name = data.topic_name

                p_guid_list = data.participant_key.value
                p_guid_int = int(''.join(map(str, p_guid_list)))

                reader = Entity(topic_name=topic_name,
                                type_name=type_name, kind="Reader", p_guid=p_guid_int)
                
                if key_int not in entities:
                    print(f"Adding Reader to list: {reader.topic_name}")
                    entities[key_int] = reader
                



def main():
    # Create participant in disabled state
    participant_factory_qos = dds.DomainParticipantFactoryQos()
    participant_factory_qos.entity_factory.autoenable_created_entities = False
    dds.DomainParticipant.participant_factory_qos = participant_factory_qos

    participant = dds.DomainParticipant(domain_id=1)

    # Set listeners for the built-in DataReaders
    participant.publication_reader.set_listener(PublicationListener(), dds.StatusMask.DATA_AVAILABLE)
    participant.subscription_reader.set_listener(SubscriptionListener(), dds.StatusMask.DATA_AVAILABLE)

    # Enable participant
    participant.enable()

    print("Participant Enabled, listening for entities")
    # Keep the application running


    
    try:
        while True:
            
            # Get current participants
            p_list = participant.discovered_participants()
            for p in p_list:
              data = participant.discovered_participant_data(p)
              name = data.participant_name.name
              ip_list = data.default_unicast_locators[0].address[-4:]
              ip = '.'.join(str(byte) for byte in ip_list)

              participant_info = Participant(name, ip)

              key_list = data.key.value
              key_int = int(''.join(map(str, key_list)))
              # print(f"Participant Key: {key_int}")
              participants[key_int] = participant_info
              # print(f'Participant Name: {data.participant_name.name}')

            # Downselect Dict for Edge matching
            readers = {k: v for k, v in entities.items() if v.kind == "Reader"}
            writers = {k: v for k, v in entities.items() if v.kind == "Writer"}

            for w in writers:
              # Update writers with Participant info
              if writers[w].p_guid in participants:
                entities[w].p_ip = participants[writers[w].p_guid].ip
                entities[w].p_name = participants[writers[w].p_guid].name
                
              # Get Edges
              for r in readers:
                if readers[r].topic_name == writers[w].topic_name and readers[r].type_name == writers[w].type_name:
                  edge_key = (w, r)
                  # print(edge_key)
                  new_edge = Edge(w, r, readers[r].topic_name)
                  edges[edge_key] = new_edge

            for r in readers:
              # Update readers with Participant info
              if readers[r].p_guid in participants:
                entities[r].p_ip = participants[readers[r].p_guid].ip
                entities[r].p_name = participants[readers[r].p_guid].name

            print(f'Discovered Entities Count: {len(entities)}')

            print(f'Discovered Participants Count: {len(p_list)}')
            for p in participants:
              print(f'Name: {participants[p].name}')
              print(f'IP: {participants[p].ip}')

            time.sleep(2)


    except KeyboardInterrupt:
      # Entities
      print("\nEXPORTING Entities")
      en_header = ["id", "topic name", "type name", "kind", "participant ip", "participant name", "participant id"]

      with open('entities.csv', 'w', newline='') as en_csvfile:
        en_writer = csv.writer(en_csvfile)
        en_writer.writerow(en_header)

        for e in entities:
          en_writer.writerow([e, entities[e].topic_name, entities[e].type_name, entities[e].kind, entities[e].p_ip, entities[e].p_name, entities[e].p_guid])

      # Participants
      print("\nEXPORTING Participants")
      dp_header = ["id", "name", "ip"]

      with open('participants.csv', 'w', newline='') as dp_csvfile:
        dp_writer = csv.writer(dp_csvfile)
        dp_writer.writerow(dp_header)

        for p in participants:
          dp_writer.writerow([p, participants[p].name, participants[p].ip])

      # Edges
      print("\nEXPORTING Edges")
      ed_header = ["id", "from", "to", "topic"]

      with open('edges.csv', 'w', newline='') as ed_csvfile:
        ed_writer = csv.writer(ed_csvfile)
        ed_writer.writerow(ed_header)

        for x in edges:
          ed_writer.writerow([x, edges[x].source, edges[x].target, edges[x].topic_name])



if __name__ == "__main__":
    main()