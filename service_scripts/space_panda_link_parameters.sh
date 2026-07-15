ros2 service call /space_panda_link/set_parameters rcl_interfaces/srv/SetParameters \
  "{parameters: [{name: 'mimicing.scale', value: {type: 3, double_value: $1}}, {name: 'wrench_passthrough.force_scale', value: {type: 3, double_value: $2}}, {name: 'wrench_passthrough.torque_scale', value: {type: 3, double_value: $3}}, {name: 'damping.value', value: {type: 3, double_value: $4}}, {name: 'mimicing.enabled', value: {type: 1, bool_value: $5}}, {name: 'wrench_passthrough.enabled', value: {type: 1, bool_value: $6}}, {name: 'damping.enabled', value: {type: 1, bool_value: $7}}]}"

