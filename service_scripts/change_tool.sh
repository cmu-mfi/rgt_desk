ros2 service call /rgt_manager/change_tool rgt_interfaces/srv/ChangeTool "{robot: $1, tool: '$2'}"
