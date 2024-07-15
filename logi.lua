-- 本脚本需配合自动识别程序使用, 且仅支持全自动武器和半自动武器单点压枪, 支持2, 3, 4倍镜和全部配件
-------------------------------------- [[全局动态注入参数 - 使用dofile更新]]
-- 枪械名字, 默认识别为空, 为空时值为"None".
GunName = "None"

-- 后坐力系数, 默认为1即满配(枪口补偿, 拇指握把, 战术枪托, 基础瞄具). 该系数为配件相关系数, 不代表最终系数, 由识别的配件相乘得出.
RecoilFactor = 1

-- 当前人物姿势, 1-站立, 2-蹲下, 3-卧倒. 不同姿势对应不同的后坐力系数
Posture = 1

-------------------------------------- [[全局动态参数 - 脚本运行时更新]]
-- 是否运行脚本, 由当前按键状态决定, 用于中断脚本
IsRun = false

-- 鼠标按下时记录脚本运行时间戳
ClickStartTime = 0

-- 当前时间戳
ClickCurrentTime = 0

-- 第几颗子弹
BulletIndex = 0
-------------------------------------- [[全局静态参数]]
-- 是否开启debug
IsDebug = false

-- 瞄准模式: 0-切换开镜, 1-长按开镜
AimingModel = 1

-- CPU负载等级, 值越大循环的频率越低, 压枪效果也越差. 提高值可以提高压枪的fps, 但也会增加CPU的计算量
CpuLoad = 2

-- 识别程序输出的脚本文件路径
ConfigPath = "C:/Users/Public/Downloads/pubg_config.lua"

-------------------------------------- [[枪械参数]]
Guns = {
    M762 = {
        interval = 86,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.55,
        recoilPattern = { 5, 5, 5, 9, 14, 20, 27, 35, 44, 54, 65, 77, 89, 101, 113, 125, 137, 148, 159, 169, 178, 186, 193, 199, 204, 208, 211, 213, 214, 214 }
    },
    AUG = {
        interval = 83,
        standingRecoilFactor = 1,
        crouchingRecoilFactor = 0.83,
        proneRecoilFactor = 0.55,
        recoilPattern = { 5, 5, 5, 9, 14, 20, 27, 35, 44, 54, 65, 77, 89, 101, 113, 125, 137, 148, 159, 169, 178, 186, 193, 199, 204, 208, 211, 213, 214, 214 }
    }
}

-------------------------------------- [[函数定义]]
-- 加载配置
function LoadConfig()
    dofile(ConfigPath)
    IsRun = true
end
-- 重置配置
function ResetConfig()
    IsRun = false
    SetRandomseed()
end
-- 更新随机数种子(reverse确保变化范围)
function SetRandomseed()
    math.randomseed(GetDate("%H%M%S"):reverse())
end
-- 随机睡眠
function RandomSleep()
    if IsDebug then
        Sleep(CpuLoad)
    else
        Sleep(math.random(CpuLoad + CpuLoad+5))
    end
end

-- 应用压枪
function ApplyRecoil(gunData, recoilFactor, posture)

	-- Accurate aiming press gun
	pubg.currentTime = GetRunningTime()

	pubg.bulletIndex = math.ceil(((pubg.currentTime - pubg.startTime == 0 and {1} or {pubg.currentTime - pubg.startTime})[1]) / options.interval) + 1

    pubg.bulletIndex = math.ceil((pubg.currentTime - pubg.startTime == 0 and 1 or pubg.currentTime - pubg.startTime) / options.interval) + 1

    -- 当前子弹序号不能超过最大值
	if pubg.bulletIndex > options.amount then return false end

	-- Developer Debugging Mode
	local d = (IsKeyLockOn("scrolllock") and { (pubg.bulletIndex - 1) * pubg.xLengthForDebug } or { 0 })[1]

	local x = math.ceil((pubg.currentTime - pubg.startTime) / (options.interval * (pubg.bulletIndex - 1)) * d) - pubg.xCounter
	local y = math.ceil((pubg.currentTime - pubg.startTime) / (options.interval * (pubg.bulletIndex - 1)) * options.ballistic[pubg.bulletIndex]) - pubg.counter


	-- 4-fold pressure gun mode
	local realY = pubg.getRealY(options, y)
	MoveMouseRelative(x, realY)

	-- Whether to issue automatically or not
	if options.autoContinuousFiring == 1 then
		PressAndReleaseMouseButton(1)
	end

	-- Real-time operation parameters
	pubg.autoLog(options, y)
	pubg.outputLogRender()

	pubg.xCounter = pubg.xCounter + x
	pubg.counter = pubg.counter + y

	pubg.autoSleep(IsKeyLockOn("scrolllock"))
end

-------------------------------------- [[开启鼠标监听]]
EnablePrimaryMouseButtonEvents(true) -- 开启鼠标左键监听
function OnEvent (event, arg, family)
    -- 按下鼠标左键, 加载配置项目 (AimingModel == 0时, 仅需按下左键, AimingModel == 1时, 需保持右键按下状态)
    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" and ((AimingModel == 1 and IsMouseButtonPressed(3)) or AimingModel == 0) then
        LoadConfig()
        if GunName ~= "None" then
            -- 记录脚本开启时间
            StartTime = GetRunningTime()
            SetMKeyState(1, "kb")
        end
    -- 松开鼠标左键, 恢复动态参数默认值
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
        ResetConfig()
    end
    -- M_PRESSED用于递归触发压枪
    if event == "M_PRESSED" and arg == 1 and IsRun and GunName ~= "None" then
        ApplyRecoil(Guns[GunName], RecoilFactor, Posture)
        SetMKeyState(1, "kb")
    end
end



	if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" then
		if not pubg.runStatus() then return false end
		if userInfo.aimingSettings ~= "default" and not IsMouseButtonPressed(3) then
			pubg.PressOrRelaseAimKey(true)
		end
		if pubg.isAimingState("ADS") or pubg.isAimingState("Aim") then
			pubg.startTime = GetRunningTime()
			pubg.G1 = true
			SetMKeyState(1, "kb")
		end
	end

	if event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
		pubg.PressOrRelaseAimKey(false)
		pubg.G1 = false
		pubg.counter = 0 -- Initialization counter
		pubg.xCounter = 0 -- Initialization xCounter
		pubg.SetRandomseed() -- Reset random number seeds
	end

	if event == "M_PRESSED" and arg == 1 and pubg.G1 then
		pubg.auto(pubg.gunOptions[pubg.bulletType][pubg.gunIndex])
		SetMKeyState(1, "kb")
	end













-- 定义武器配件的修正系数
local attachment_multipliers = {
    poses = {
        None = 1,
        stand = 1,
        down = 0.83,
        lie = 0.83,
    },
    muzzles_rifle = {
        None = 1,
        buchang = 0.79,
        xiaoyan = 0.855,
    },
    grips_rifle = {
        None = 1,
        qingxing = 0.85,
        chuizhi = 0.792,
        banjie = 0.83,
        muzhi = 0.9,
    },
    scopes_rifle = {
        None = 1,
        reddot = 1,
        quanxi = 1,
        x2 = 1.24,
        x3 = 1.65,
        x4 = 2.2,
        x6 = 1.65,
        x8 = 0.9,
    },
    stocks_rifle = {
        None = 1,
        zhongxing = 1,
        zhanshu = 1,
    }
}


-- 累计小数部分
local decimal_cache = 0

-- 向上取整并缓存小数部分
function ceil_and_cache(value)
    local integer_part = math.floor(value)
    decimal_cache = decimal_cache + value - integer_part
    if decimal_cache >= 1 then
        integer_part = integer_part + 1
        decimal_cache = decimal_cache - 1
    end
    return integer_part
end

-- 计算修正系数
function calculate_recoil_multiplier(poses, muzzles, grips, scopes, stocks, weapon_type)
    local multiplier = 1

    multiplier = multiplier * (attachment_multipliers["muzzles_"..weapon_type][muzzles] or 1)
    multiplier = multiplier * (attachment_multipliers["grips_"..weapon_type][grips] or 1)
    multiplier = multiplier * (attachment_multipliers["scopes_"..weapon_type][scopes] or 1)
    multiplier = multiplier * (attachment_multipliers["stocks_"..weapon_type][stocks] or 1)
    multiplier = multiplier * (attachment_multipliers.poses[poses] or 1)

    if IsModifierPressed("ralt") then
        multiplier = multiplier * (attachment_multipliers.poses.down or 1)
    end

    return multiplier
end

-- 定义全局变量来控制非 MK47/M16 枪械的连点模式
local burstModeEnabled = false

-- 应用压枪
function apply_recoil(weapon_name, posture_state, muzzles, grips, scopes, stocks, weapon_type)
    local pattern = recoil_patterns[weapon_name]
    local interval = weapon_intervals[weapon_name]
    if not pattern then
        OutputLogMessage("未找到武器的压枪参数: %s\n", weapon_name)
        return
    end

    local multiplier = calculate_recoil_multiplier(posture_state, muzzles, grips, scopes, stocks, weapon_type)
    local bullet_count = 0

    if weapon_name == "MK47" or weapon_name == "M16" then
        -- MK47 和 M16 特殊处理
        local isFirstClick = true
        for i, recoil_data in ipairs(pattern) do
            if IsMouseButtonPressed(3) or IsMouseButtonPressed(4)then
                bullet_count = bullet_count + 1
                if bullet_count == recoil_data[1] then
                    local adjusted_recoil = ceil_and_cache(recoil_data[2] * multiplier)
                    MoveMouseRelative(0, adjusted_recoil)
                    Sleep(interval)
                     PressAndReleaseMouseButton(1)
            end
        end
    end

    elseif burstModeEnabled then
        -- 其他枪械在开启连点模式后才进行连点压枪
        for i, recoil_data in ipairs(pattern) do
            if IsMouseButtonPressed(3) then
                bullet_count = bullet_count + 1
                if bullet_count == recoil_data[1] then
                    local adjusted_recoil = ceil_and_cache(recoil_data[2] * multiplier)
                    MoveMouseRelative(0, adjusted_recoil)
                    Sleep(interval)
                    PressAndReleaseMouseButton(1)  -- 连点
                end
            else
                break
            end
        end
    else
        -- 其他枪械的默认压枪处理（不连点）
        for i, recoil_data in ipairs(pattern) do
            if IsMouseButtonPressed(3) then
                bullet_count = bullet_count + 1
                if bullet_count == recoil_data[1] then
                    local adjusted_recoil = ceil_and_cache(recoil_data[2] * multiplier)
                    MoveMouseRelative(0, adjusted_recoil)
                    Sleep(interval)
                    if not IsMouseButtonPressed(1) then
                        break
                    end
                end
            else
                break
            end
        end
    end
end

-- 读取武器信息
function read_weapon_from_file()
    -- 清除之前的武器信息
    weapon_name, posture_state = nil, nil
    muzzles_rifle, grips_rifle, scopes_rifle, stocks_rifle = nil, nil, nil, nil

    -- 读取新的武器信息
    dofile("C:/Users/Public/Downloads/pubg_state.lua")

    if weapon_name then
        local output = weapon_name .. "+" .. posture_state .. "+" .. muzzles_rifle .. "+" .. grips_rifle .. "+" .. scopes_rifle .. "+" .. stocks_rifle
        OutputLogMessage("%s\n", output)
        return weapon_name, posture_state, muzzles_rifle, grips_rifle, scopes_rifle, stocks_rifle, "rifle"
    else
        OutputLogMessage("未找到武器信息\n")
        return nil, nil, nil, nil, nil, nil, nil
    end
end

-- 事件处理函数
function OnEvent(event, arg)
    if event == "MOUSE_BUTTON_PRESSED" then
        if arg == 1 and (IsMouseButtonPressed(3) or IsMouseButtonPressed(4)) then
            local weapon_name, posture_state, muzzles, grips, scopes, stocks, weapon_type = read_weapon_from_file()
            if weapon_name then
                apply_recoil(weapon_name, posture_state, muzzles, grips, scopes, stocks, weapon_type)
            end
        end
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 then
        MoveMouseRelative(0, 0)
        continueClicking = false
    elseif event == "MOUSE_BUTTON_RELEASED" and (arg == 3 or arg == 4) then
        continueClicking = false
    end
end
