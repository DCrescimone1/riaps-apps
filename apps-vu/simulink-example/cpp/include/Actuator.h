//
// Auto-generated by edu.vanderbilt.riaps.generator.ComponenetGenerator.xtend
//
#ifndef RIAPS_FW_ACTUATOR_H
#define RIAPS_FW_ACTUATOR_H

#include "ActuatorBase.h"

namespace sltest {
   namespace components {
      
      class Actuator : public ActuatorBase {
         
         public:
         
         Actuator(_component_conf &config, riaps::Actor &actor);
         
         virtual void OnForce(const ForceType::Reader &message,
         riaps::ports::PortBase *port);
         
         void OnGroupMessage(const riaps::groups::GroupId& groupId, capnp::FlatArrayMessageReader& capnpreader, riaps::ports::PortBase* port);
         
         virtual ~Actuator();

         private:

         int sockfd=-1;
         addrinfo hints;
         addrinfo* res=0;
         
      };
   }
}

extern "C" riaps::ComponentBase* create_component(_component_conf&, riaps::Actor& actor);
extern "C" void destroy_component(riaps::ComponentBase*);


#endif //RIAPS_FW_ACTUATOR_H
