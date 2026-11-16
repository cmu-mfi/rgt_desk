<script setup>
import { computed } from 'vue';
import { AudioLines, Bot, Camera, CircleDot, Cpu, Gamepad2, Hand, House, Link, Network, Panda, Plug, Radio, ScanLine, Settings2, Thermometer, Video, Wrench } from '@lucide/vue';
const props = defineProps({ id: { type: String, required: true } });
const icons = { ur20: Bot, nex10: Bot, rgt_manager: Cpu, foxglove_bridge: Network, bed_side_cam: Camera, bed_side_thermal: Thermometer, bed_side_audio: AudioLines, gripper: Hand, tool_side_cam: Camera, tool_side_gelsight: ScanLine, spacemouse: Gamepad2, home: House, park: CircleDot, change_tool: Wrench, override_tool_location: Settings2, set_io: Plug, rosbag_record: Video, panda: Panda, space_panda_link: Link, space_panda_link_parameters: Settings2 };
const icon = computed(() => icons[props.id] ?? Radio);
</script>
<template><span class="panel-icon"><component :is="icon" :size="20" :stroke-width="1.6" /></span></template>
