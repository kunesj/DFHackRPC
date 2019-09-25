#!/usr/bin/env python3
# encoding: utf-8

# [method, input_msg, output_msg, plugin, assigned_id]
DEFAULT_METHODS = [
    # dfhack/library/proto/CoreProtocol.proto
    ['BindMethod', 'dfproto.CoreBindRequest', 'dfproto.CoreBindReply', None, 0],  # reserved ID
    ['RunCommand', 'dfproto.CoreRunCommandRequest', 'dfproto.EmptyMessage', None, 1],  # reserved ID
    ['CoreSuspend', 'dfproto.EmptyMessage', 'dfproto.IntMessage', None, None],
    ['CoreResume', 'dfproto.EmptyMessage', 'dfproto.IntMessage', None, None],
    ['RunLua', 'dfproto.CoreRunLuaRequest', 'dfproto.StringListMessage', None, None],

    # dfhack/library/proto/BasicApi.proto
    ['GetVersion', 'dfproto.EmptyMessage', 'dfproto.StringMessage', None, None],
    ['GetDFVersion', 'dfproto.EmptyMessage', 'dfproto.StringMessage', None, None],
    ['GetWorldInfo', 'dfproto.EmptyMessage', 'dfproto.GetWorldInfoOut', None, None],
    ['ListEnums', 'dfproto.EmptyMessage', 'dfproto.ListEnumsOut', None, None],
    ['ListJobSkills', 'dfproto.EmptyMessage', 'dfproto.ListJobSkillsOut', None, None],
    ['ListMaterials', 'dfproto.ListMaterialsIn', 'dfproto.ListMaterialsOut', None, None],
    ['ListUnits', 'dfproto.ListUnitsIn', 'dfproto.ListUnitsOut', None, None],
    ['ListSquads', 'dfproto.ListSquadsIn', 'dfproto.ListSquadsOut', None, None],
    ['SetUnitLabors', 'dfproto.SetUnitLaborsIn', 'dfproto.EmptyMessage', None, None],

    # dfhack/plugins/proto/rename.proto
    ['RenameSquad', 'dfproto.RenameSquadIn', 'dfproto.EmptyMessage', 'rename', None],
    ['RenameUnit', 'dfproto.RenameUnitIn', 'dfproto.EmptyMessage', 'rename', None],
    ['RenameBuilding', 'dfproto.RenameBuildingIn', 'dfproto.EmptyMessage', 'rename', None],

    # dfhack/plugins/proto/isoworldremote.proto
    ['GetEmbarkTile', 'isoworldremote.TileRequest', 'isoworldremote.EmbarkTile', 'isoworldremote', None],
    ['GetEmbarkInfo', 'isoworldremote.MapRequest', 'isoworldremote.MapReply', 'isoworldremote', None],
    ['GetRawNames', 'isoworldremote.MapRequest', 'isoworldremote.RawNames', 'isoworldremote', None],

    # dfhack/plugins/proto/RemoteFortressReader.proto
    ['GetMaterialList', 'dfproto.EmptyMessage', 'RemoteFortressReader.MaterialList', 'RemoteFortressReader', None],
    ['GetGrowthList', 'dfproto.EmptyMessage', 'RemoteFortressReader.MaterialList', 'RemoteFortressReader', None],
    ['GetBlockList', 'RemoteFortressReader.BlockRequest', 'RemoteFortressReader.BlockList', 'RemoteFortressReader', None],
    ['CheckHashes', 'dfproto.EmptyMessage', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['GetTiletypeList', 'dfproto.EmptyMessage', 'RemoteFortressReader.TiletypeList', 'RemoteFortressReader', None],
    ['GetPlantList', 'RemoteFortressReader.BlockRequest', 'RemoteFortressReader.PlantList', 'RemoteFortressReader', None],
    ['GetUnitList', 'dfproto.EmptyMessage', 'RemoteFortressReader.UnitList', 'RemoteFortressReader', None],
    ['GetUnitListInside', 'RemoteFortressReader.BlockRequest', 'RemoteFortressReader.UnitList', 'RemoteFortressReader', None],
    ['GetViewInfo', 'dfproto.EmptyMessage', 'RemoteFortressReader.ViewInfo', 'RemoteFortressReader', None],
    ['GetMapInfo', 'dfproto.EmptyMessage', 'RemoteFortressReader.MapInfo', 'RemoteFortressReader', None],
    ['ResetMapHashes', 'dfproto.EmptyMessage', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['GetItemList', 'dfproto.EmptyMessage', 'RemoteFortressReader.MaterialList', 'RemoteFortressReader', None],
    ['GetBuildingDefList', 'dfproto.EmptyMessage', 'RemoteFortressReader.BuildingList', 'RemoteFortressReader', None],
    ['GetWorldMap', 'dfproto.EmptyMessage', 'RemoteFortressReader.WorldMap', 'RemoteFortressReader', None],
    ['GetWorldMapNew', 'dfproto.EmptyMessage', 'RemoteFortressReader.WorldMap', 'RemoteFortressReader', None],
    ['GetRegionMaps', 'dfproto.EmptyMessage', 'RemoteFortressReader.RegionMaps', 'RemoteFortressReader', None],
    ['GetRegionMapsNew', 'dfproto.EmptyMessage', 'RemoteFortressReader.RegionMaps', 'RemoteFortressReader', None],
    ['GetCreatureRaws', 'dfproto.EmptyMessage', 'RemoteFortressReader.CreatureRawList', 'RemoteFortressReader', None],
    ['GetPartialCreatureRaws', 'RemoteFortressReader.ListRequest', 'RemoteFortressReader.CreatureRawList', 'RemoteFortressReader', None],
    ['GetWorldMapCenter', 'dfproto.EmptyMessage', 'RemoteFortressReader.WorldMap', 'RemoteFortressReader', None],
    ['GetPlantRaws', 'dfproto.EmptyMessage', 'RemoteFortressReader.PlantRawList', 'RemoteFortressReader', None],
    ['GetPartialPlantRaws', 'RemoteFortressReader.ListRequest', 'RemoteFortressReader.PlantRawList', 'RemoteFortressReader', None],
    ['CopyScreen', 'dfproto.EmptyMessage', 'RemoteFortressReader.ScreenCapture', 'RemoteFortressReader', None],
    ['PassKeyboardEvent', 'RemoteFortressReader.KeyboardEvent', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['SendDigCommand', 'RemoteFortressReader.DigCommand', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['SetPauseState', 'RemoteFortressReader.SingleBool', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['GetPauseState', 'dfproto.EmptyMessage', 'RemoteFortressReader.SingleBool', 'RemoteFortressReader', None],
    ['GetVersionInfo', 'dfproto.EmptyMessage', 'RemoteFortressReader.VersionInfo', 'RemoteFortressReader', None],
    ['GetReports', 'dfproto.EmptyMessage', 'RemoteFortressReader.Status', 'RemoteFortressReader', None],
    ['MoveCommand', 'AdventureControl.MoveCommandParams', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['JumpCommand', 'AdventureControl.MoveCommandParams', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['MenuQuery', 'dfproto.EmptyMessage', 'AdventureControl.MenuContents', 'RemoteFortressReader', None],
    ['MovementSelectCommand', 'dfproto.IntMessage', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['MiscMoveCommand', 'AdventureControl.MiscMoveParams', 'dfproto.EmptyMessage', 'RemoteFortressReader', None],
    ['GetLanguage', 'dfproto.EmptyMessage', 'RemoteFortressReader.Language', 'RemoteFortressReader', None],
]
