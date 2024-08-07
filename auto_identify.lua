--[[本脚本需配合自动识别程序使用, 且仅支持全自动武器和半自动武器单点压枪, 支持2, 3, 4倍镜和全部配件]]
-- 垂直灵敏度影响 : 1 / 垂灵
-- 配件相乘 -5后坐力等于少百分之7 每1后坐力减少1.4百分比 每1回复减少0.7百分比

--[[-----------------------------------------------------------全局动态注入参数 - 使用dofile更新-----------------------------------------------------------]]

-- 枪械名字, 默认识别为空, 为空时值为"None".
GunName = "None"
-- 后坐力系数, 默认为游戏内灵敏度1 * 配件系数 * 倍镜系数 * 姿势系数
RecoilCoefficient = 1

--[[-----------------------------------------------------------全局动态参数 - 脚本运行时更新-----------------------------------------------------------]]

-- 是否运行脚本, 由当前按键状态决定, 用于中断脚本
IsRun = false
-- 鼠标按下时记录脚本运行时间戳
ClickStartTime = 0
-- 当前时间戳
ClickCurrentTime = 0
-- 第几颗子弹
BulletIndex = 0
XCounter = 0
YCounter = 0

--[[---------------------------------------------------------------全局静态参数---------------------------------------------------------------]]

-- 是否开启debug
IsDebug = false
-- 瞄准模式: 0-切换开镜, 1-长按开镜
AimingModel = 1
-- 循环延迟, 值越大循环的频率越低, 屏幕抖动越厉害
CycleDelay = 3
-- 识别程序输出的脚本文件路径
ConfigPath = "C:/Users/Public/Downloads/pubg_config.lua"

--[[---------------------------------------------------------------枪械参数---------------------------------------------------------------]]

Guns = {
    akm = {
        ads = 100,
        interval = 100,
        ballistics = {},
        recoilPattern = {
            { 1, 21 },
            { 2, 15 },
            { 3, 16 },
            { 4, 16 },
            { 5, 19 },
            { 6, 20 },
            { 7, 21 },
            { 8, 22 },
            { 9, 21 },
            { 10, 21 },
            { 11, 24 },
            { 12, 26 },
            { 13, 26 },
            { 14, 25 },
            { 15, 25 },
            { 16, 25 },
            { 17, 26 },
            { 18, 25 },
            { 39, 29 },
            { 40, 29 }
        }
    },
    qbz = {
        ads = 100,
        interval = 92,
        ballistics = {},
        recoilPattern = {
            { 1, 22 },
            { 4, 12 },
            { 9, 14 },
            { 14, 21 },
            { 19, 22 },
            { 39, 23 }
        }
    },
    m762 = {
        ads = 100,
        interval = 86,
        ballistics = {},
        recoilPattern = {
            { 1, 26 },
            { 2, 17 },
            { 3, 18 },
            { 4, 18 },
            { 5, 22 },
            { 6, 23 },
            { 7, 24 },
            { 8, 24 },
            { 9, 24 },
            { 10, 24 },
            { 11, 27 },
            { 12, 29 },
            { 13, 29 },
            { 14, 28 },
            { 15, 28 },
            { 16, 28 },
            { 17, 30 },
            { 18, 28 },
            { 19, 33 },
            { 26, 31 },
            { 32, 30 },
            { 42, 12 }
        }
    },
    groza = {
        ads = 100,
        interval = 80,
        ballistics = {},
        recoilPattern = {
            { 1, 18 },
            { 2, 10 },
            { 3, 12 },
            { 4, 11 },
            { 5, 15 },
            { 6, 10 },
            { 7, 14 },
            { 8, 14 },
            { 9, 15 },
            { 10, 15 },
            { 11, 16 },
            { 12, 18 },
            { 13, 18 },
            { 14, 19 },
            { 15, 19 },
            { 16, 19 },
            { 17, 19 },
            { 18, 19 },
            { 19, 19 },
            { 20, 20 },
            { 21, 22 },
            { 22, 21 },
            { 23, 19 },
            { 24, 22 },
            { 25, 21 },
            { 26, 20 },
            { 27, 20 },
            { 28, 22 },
            { 29, 22 },
            { 30, 22 },
            { 31, 18 },
            { 32, 18 },
            { 33, 18 },
            { 34, 18 },
            { 35, 19 },
            { 36, 19 },
            { 37, 20 },
            { 38, 20 },
            { 40, 20 }
        }
    },
    scarl = {
        ads = 100,
        interval = 92,
        ballistics = {},
        recoilPattern = {
            { 1, 11 },
            { 2, 11 },
            { 3, 11 },
            { 4, 11 },
            { 5, 14 },
            { 6, 14 },
            { 7, 14 },
            { 8, 14 },
            { 9, 18 },
            { 10, 18 },
            { 11, 18 },
            { 12, 18 },
            { 13, 20 },
            { 37, 20 },
            { 38, 25 },
            { 39, 25 },
            { 40, 25 },
            { 42, 25 }
        }
    },
    m16a4 = {
        ads = 100,
        interval = 86,
        ballistics = {},
        recoilPattern = {
            { 1, 8 },
            { 2, 8 },
            { 3, 12 },
            { 4, 14 },
            { 5, 16 },
            { 6, 16 },
            { 7, 16 },
            { 8, 16 },
            { 9, 18 },
            { 10, 18 },
            { 11, 18 },
            { 12, 17 },
            { 13, 17 },
            { 14, 19 },
            { 15, 18 },
            { 16, 18 },
            { 17, 18 },
            { 18, 16 },
            { 19, 16 },
            { 20, 16 },
            { 21, 17 },
            { 22, 17 },
            { 23, 17 },
            { 24, 17 },
            { 25, 17 },
            { 26, 17 },
            { 27, 17 },
            { 28, 16 },
            { 29, 16 },
            { 30, 16 },
            { 31, 16 },
            { 32, 16 },
            { 33, 16 },
            { 34, 16 },
            { 35, 16 },
            { 36, 16 },
            { 37, 16 },
            { 38, 16 },
            { 40, 16 }
        }
    },
    aug = {
        ads = 100,
        interval = 83,
        ballistics = {},
        recoilPattern = {
            { 1, 21 },
            { 2, 9 },
            { 3, 12 },
            { 4, 14 },
            { 5, 17 },
            { 6, 18 },
            { 7, 18 },
            { 8, 18 },
            { 9, 19 },
            { 10, 21 },
            { 11, 25 },
            { 12, 25 },
            { 13, 25 },
            { 14, 25 },
            { 15, 25 },
            { 16, 25 },
            { 17, 25 },
            { 18, 25 },
            { 19, 25 },
            { 20, 25 },
            { 21, 28 },
            { 22, 28 },
            { 23, 28 },
            { 24, 28 },
            { 25, 28 },
            { 26, 29 },
            { 27, 29 },
            { 28, 29 },
            { 29, 29 },
            { 30, 29 },
            { 31, 29 },
            { 32, 29 },
            { 33, 29 },
            { 34, 29 },
            { 35, 29 },
            { 36, 30 },
            { 37, 30 },
            { 38, 30 },
            { 39, 30 },
            { 40, 30 },
            { 42, 30 }
        }
    },
    m416 = {
        ads = 100,
        interval = 86,
        ballistics = {},
        recoilPattern = {
            { 1, 23 },
            { 2, 10 },
            { 3, 14 },
            { 4, 17 },
            { 5, 15 },
            { 6, 17 },
            { 7, 18 },
            { 8, 18 },
            { 9, 19 },
            { 10, 19 },
            { 11, 19 },
            { 12, 19 },
            { 13, 20 },
            { 14, 20 },
            { 15, 20 },
            { 16, 20 },
            { 17, 20 },
            { 18, 20 },
            { 19, 20 },
            { 20, 21 },
            { 21, 20 },
            { 22, 21 },
            { 23, 23 },
            { 24, 24 },
            { 25, 25 },
            { 26, 22 },
            { 27, 26 },
            { 28, 22 },
            { 29, 23 },
            { 30, 23 },
            { 31, 23 },
            { 32, 23 },
            { 33, 23 },
            { 34, 23 },
            { 35, 23 },
            { 36, 23 },
            { 37, 23 },
            { 38, 23 },
            { 41, 23 }
        }
    },
    k2 = {
        ads = 100,
        interval = 86,
        ballistics = {},
        recoilPattern = {
            { 1, 37 },
            { 2, 25 },
            { 3, 32 },
            { 4, 34 },
            { 5, 37 },
            { 6, 38 },
            { 7, 42 },
            { 8, 44 },
            { 9, 44 },
            { 10, 45 },
            { 11, 47 },
            { 12, 45 },
            { 13, 49 },
            { 14, 47 },
            { 19, 55 },
            { 26, 53 },
            { 32, 50 },
            { 42, 20 }
        }
    },
    g36c = {
        ads = 100,
        interval = 86,
        ballistics = {},
        recoilPattern = {
            { 1, 12 },
            { 4, 16 },
            { 9, 17 },
            { 14, 20 },
            { 19, 23 },
            { 39, 24 }
        }
    },
    mk47 = {
        ads = 100,
        interval = 90,
        ballistics = {},
        recoilPattern = {
            { 1, 17 },
            { 7, 17 },
            { 11, 20 },
            { 18, 21 },
            { 32, 22 }
        }
    },
    ace32 = {
        ads = 100,
        interval = 88,
        ballistics = {},
        recoilPattern = {
            { 1, 21 },
            { 2, 15 },
            { 3, 15 },
            { 4, 18 },
            { 5, 19 },
            { 6, 19 },
            { 7, 21 },
            { 8, 21 },
            { 9, 21 },
            { 10, 21 },
            { 11, 22 },
            { 12, 23 },
            { 13, 23 },
            { 14, 24 },
            { 19, 24 },
            { 20, 25 },
            { 40, 27 }
        }
    },
    ump = {
        ads = 100,
        interval = 90,
        ballistics = {},
        recoilPattern = {
            { 1, 37 },
            { 2, 25 },
            { 3, 32 },
            { 4, 34 },
            { 5, 37 },
            { 6, 38 },
            { 7, 42 },
            { 8, 44 },
            { 9, 44 },
            { 10, 45 },
            { 11, 47 },
            { 12, 45 },
            { 13, 49 },
            { 14, 47 },
            { 19, 55 },
            { 26, 53 },
            { 32, 50 },
            { 42, 20 }
        }
    },
    mp5k = {
        ads = 100,
        interval = 67,
        ballistics = {},
        recoilPattern = {
            { 1, 37 },
            { 2, 25 },
            { 3, 32 },
            { 4, 34 },
            { 5, 37 },
            { 6, 38 },
            { 7, 42 },
            { 8, 44 },
            { 9, 44 },
            { 10, 45 },
            { 11, 47 },
            { 12, 45 },
            { 13, 49 },
            { 14, 47 },
            { 19, 55 },
            { 26, 53 },
            { 32, 50 },
            { 42, 20 }
        }
    },
    vkt = {
        ads = 100,
        interval = 54,
        ballistics = {},
        recoilPattern = {
            { 1, 37 },
            { 2, 25 },
            { 3, 32 },
            { 4, 34 },
            { 5, 37 },
            { 6, 38 },
            { 7, 42 },
            { 8, 44 },
            { 9, 44 },
            { 10, 45 },
            { 11, 47 },
            { 12, 45 },
            { 13, 49 },
            { 14, 47 },
            { 19, 55 },
            { 26, 53 },
            { 32, 50 },
            { 42, 20 }
        }
    },
    p90 = {
        ads = 100,
        interval = 60,
        ballistics = {},
        recoilPattern = {
            { 1, 19 },
            { 2, 17 },
            { 3, 14 },
            { 4, 17 },
            { 5, 20 },
            { 6, 13 },
            { 7, 24 },
            { 8, 16 },
            { 9, 22 },
            { 10, 23 },
            { 11, 18 },
            { 12, 31 },
            { 13, 17 },
            { 14, 26 },
            { 15, 24 },
            { 16, 12 },
            { 17, 26 },
            { 18, 9 },
            { 19, 22 },
            { 20, 14 },
            { 21, 6 },
            { 22, 26 },
            { 23, 17 },
            { 24, 11 },
            { 25, 6 },
            { 26, 18 },
            { 27, 3 },
            { 28, 16 },
            { 29, 10 },
            { 30, 8 },
            { 31, 22 },
            { 32, 21 },
            { 33, 12 },
            { 34, 7 },
            { 35, 26 },
            { 36, 8 },
            { 37, 15 },
            { 38, 11 },
            { 39, 10 },
            { 40, 17 },
            { 41, 4 },
            { 42, 26 },
            { 43, 9 },
            { 44, 9 },
            { 45, 22 },
            { 46, 7 },
            { 47, 25 }
        }
    },
    m249 = {
        ads = 100,
        interval = 75,
        ballistics = {},
        recoilPattern = {
            { 1, 15 },
            { 2, 5 },
            { 3, 8 },
            { 4, 5 },
            { 5, 13 },
            { 6, 13 },
            { 7, 15 },
            { 8, 17 },
            { 9, 17 },
            { 10, 15 },
            { 11, 15 },
            { 12, 13 },
            { 13, 12 },
            { 14, 11 },
            { 15, 11 },
            { 16, 9 },
            { 17, 9 },
            { 18, 8 },
            { 19, 8 },
            { 20, 9 },
            { 21, 9 },
            { 22, 8 },
            { 23, 8 },
            { 24, 8 },
            { 25, 9 },
            { 26, 9 },
            { 27, 9 },
            { 28, 9 },
            { 29, 9 },
            { 30, 9 },
            { 31, 9 },
            { 32, 9 },
            { 33, 9 },
            { 34, 8 },
            { 35, 8 },
            { 36, 8 },
            { 37, 8 },
            { 38, 8 },
            { 39, 8 },
            { 40, 9 },
            { 41, 9 },
            { 42, 9 },
            { 43, 9 },
            { 44, 9 },
            { 45, 9 },
            { 46, 9 },
            { 47, 9 },
            { 48, 9 },
            { 49, 9 },
            { 50, 9 },
            { 51, 9 },
            { 52, 9 },
            { 53, 9 },
            { 54, 9 },
            { 55, 9 },
            { 56, 9 },
            { 57, 9 },
            { 58, 9 },
            { 59, 9 },
            { 60, 9 },
            { 61, 9 },
            { 62, 9 },
            { 63, 9 },
            { 64, 9 },
            { 65, 9 },
            { 66, 9 },
            { 67, 8 },
            { 68, 9 },
            { 69, 9 },
            { 70, 9 },
            { 71, 9 },
            { 72, 9 },
            { 73, 9 },
            { 74, 9 },
            { 75, 9 },
            { 76, 9 },
            { 77, 9 },
            { 78, 9 },
            { 79, 9 },
            { 80, 9 },
            { 81, 9 },
            { 82, 9 },
            { 83, 9 },
            { 84, 9 },
            { 85, 9 },
            { 86, 9 },
            { 87, 9 },
            { 88, 9 },
            { 89, 9 },
            { 90, 9 },
            { 91, 9 },
            { 92, 9 },
            { 93, 9 },
            { 94, 9 },
            { 95, 9 },
            { 96, 9 },
            { 97, 9 },
            { 98, 9 },
            { 99, 9 },
            { 100, 9 },
            { 101, 10 },
            { 102, 10 },
            { 103, 10 },
            { 104, 10 },
            { 105, 10 },
            { 106, 10 },
            { 107, 10 },
            { 108, 10 },
            { 109, 10 },
            { 110, 10 },
            { 111, 10 },
            { 112, 10 },
            { 113, 10 },
            { 114, 10 },
            { 115, 10 },
            { 116, 10 },
            { 117, 10 },
            { 118, 10 },
            { 119, 10 },
            { 120, 10 },
            { 121, 9 },
            { 122, 9 },
            { 123, 9 },
            { 124, 9 },
            { 125, 9 },
            { 126, 9 },
            { 127, 9 },
            { 128, 9 },
            { 129, 9 },
            { 130, 9 },
            { 131, 9 },
            { 132, 9 },
            { 133, 9 },
            { 134, 9 },
            { 135, 9 },
            { 136, 9 },
            { 137, 9 },
            { 138, 9 },
            { 139, 9 },
            { 140, 9 },
            { 141, 9 },
            { 142, 9 },
            { 143, 9 },
            { 144, 9 },
            { 145, 9 },
            { 146, 9 },
            { 147, 9 },
            { 148, 9 },
            { 149, 9 },
            { 150, 9 },
            { 151, 9 },
            { 152, 9 },
            { 153, 9 },
            { 154, 9 },
            { 155, 9 },
            { 156, 9 },
            { 157, 9 },
            { 158, 9 },
            { 159, 9 }
        }
    },
    dp28 = {
        ads = 100,
        interval = 109,
        ballistics = {},
        recoilPattern = {
            { 1, 23 },
            { 2, 12 },
            { 3, 14 },
            { 4, 20 },
            { 5, 22 },
            { 6, 22 },
            { 7, 28 },
            { 8, 28 },
            { 9, 29 },
            { 10, 39 },
            { 11, 28 },
            { 12, 36 },
            { 13, 36 },
            { 14, 36 },
            { 15, 36 },
            { 16, 36 },
            { 17, 36 },
            { 18, 36 },
            { 19, 36 },
            { 20, 36 },
            { 21, 36 },
            { 22, 36 },
            { 23, 36 },
            { 24, 36 },
            { 25, 36 },
            { 26, 36 },
            { 27, 36 },
            { 28, 36 },
            { 29, 36 },
            { 30, 36 },
            { 31, 36 },
            { 32, 36 },
            { 33, 36 },
            { 34, 36 },
            { 35, 36 },
            { 36, 36 },
            { 37, 36 },
            { 38, 36 },
            { 39, 36 },
            { 40, 36 },
            { 41, 36 },
            { 42, 36 },
            { 43, 36 },
            { 44, 36 },
            { 45, 36 },
            { 46, 36 },
            { 47, 36 }
        }
    },
    mg3 = {
        ads = 100,
        interval = 91,
        ballistics = {},
        recoilPattern = {
            { 1, 37 },
            { 2, 25 },
            { 3, 32 },
            { 4, 34 },
            { 5, 37 },
            { 6, 38 },
            { 7, 42 },
            { 8, 44 },
            { 9, 44 },
            { 10, 45 },
            { 11, 47 },
            { 12, 45 },
            { 13, 49 },
            { 14, 47 },
            { 19, 55 },
            { 26, 53 },
            { 32, 50 },
            { 42, 20 }
        }
    },
    famae = {
        ads = 100,
        interval = 67,
        ballistics = {},
        recoilPattern = {
            { 1, 37 },
            { 2, 25 },
            { 3, 32 },
            { 4, 34 },
            { 5, 37 },
            { 6, 38 },
            { 7, 42 },
            { 8, 44 },
            { 9, 44 },
            { 10, 45 },
            { 11, 47 },
            { 12, 45 },
            { 13, 49 },
            { 14, 47 },
            { 19, 55 },
            { 26, 53 },
            { 32, 50 },
            { 42, 20 }
        }
    }
}

--[[---------------------------------------------------------------函数定义---------------------------------------------------------------]]

-- 加载配置
function LoadConfig()
    dofile(ConfigPath)
    IsRun = true
end

-- 重置配置
function ResetConfig()
    IsRun = false
    XCounter = 0
    YCounter = 0
    ClickCurrentTime = 0
    SetRandomseed()
end

-- 更新随机数种子(reverse确保变化范围)
function SetRandomseed()
    math.randomseed(GetDate("%H%M%S"):reverse())
end

-- 随机睡眠
function RandomSleep()
    if IsDebug then
        Sleep(CycleDelay)
    else
        Sleep(math.random(CycleDelay, CycleDelay + 3))
    end
end

-- 填充后坐力列表
function FillGaps(recoilPattern)
    local newPattern = {}
    local lastIndex = 0

    for i, pair in ipairs(recoilPattern) do
        local index = pair[1]
        local value = pair[2]

        if index > lastIndex + 1 then
            for j = lastIndex + 1, index - 1 do
                table.insert(newPattern, { j, recoilPattern[i - 1][2] })
            end
        end

        table.insert(newPattern, { index, value })
        lastIndex = index
    end

    return newPattern
end

-- 去除子弹坐标
function ExtractValues(ads, recoilPattern)
    local values = {}
    for i, pair in ipairs(recoilPattern) do
        table.insert(values, MathRound(pair[2] * ads / 100, 2))
    end
    return values
end

-- 四舍五入
function MathRound(number, decimals)
    local power = 10 ^ decimals
    return math.floor(number * power + 0.5) / power
end

-- 转换至后坐力序列
function AccumulateValues(values, coefficient)
    local accumulated = {}
    local sum = 0
    for _, value in ipairs(values) do
        sum = MathRound(sum + (value * coefficient), 2)
        table.insert(accumulated, sum)
    end
    return accumulated
end

-- 压枪
function ApplyRecoil(gunData, bulletIndex)
    local x = 0
    if IsDebug then
        x = math.ceil((ClickCurrentTime - ClickStartTime) / (gunData.interval * (bulletIndex)) * bulletIndex * 20) -
            XCounter
    end
    local y = math.ceil((ClickCurrentTime - ClickStartTime) / (gunData.interval * bulletIndex) *
        gunData.ballistics[bulletIndex]) - YCounter
    MoveMouseRelative(x, y)
    if IsDebug then
        OutputLogMessage("MoveMouseRelative ====> " .. "=== x: " .. x .. " === y: " .. y .. "\n")
    end

    XCounter = XCounter + x
    YCounter = YCounter + y
    RandomSleep()
end

-- 弹道初始化
function BallisticInitialization()
    OutputLogMessage("> Ballistic initialization Begin..." .. "\n")
    for name, gun in pairs(Guns) do
        gun.recoilPattern = ExtractValues(gun.ads, FillGaps(gun.recoilPattern))
        if IsDebug then
            OutputLogMessage("> " .. name .. "   ==> " .. table.concat(gun.recoilPattern, ", ") .. "\n")
            OutputLogMessage("\n")
        end
    end
    OutputLogMessage("> Ballistic initialization end" .. "\n")
end

--[[---------------------------------------------------------------预处理---------------------------------------------------------------]]
EnablePrimaryMouseButtonEvents(true)
BallisticInitialization()

--[[---------------------------------------------------------------开启监听---------------------------------------------------------------]]
function OnEvent(event, arg, family)
    if IsDebug then
        OutputLogMessage("start => " .. "event: " .. event .. " arg: " .. arg .. "\n")
    end
    -- 按下鼠标左键, 加载配置项目 (AimingModel == 0时, 仅需按下左键, AimingModel == 1时, 需保持右键按下状态)
    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and family == "mouse" then
        -- 记录脚本开启时间
        ClickStartTime = GetRunningTime()
        Sleep(1)
        if (AimingModel == 1 and IsMouseButtonPressed(3)) or AimingModel == 0 then
            LoadConfig()
            if GunName ~= "None" then
                if GunName ~= "mk47" and GunName ~= "m16a4" then
                    local gunData = Guns[GunName]
                    -- 计算弹道
                    gunData.ballistics = AccumulateValues(gunData.recoilPattern, RecoilCoefficient)
                    local count = #gunData.ballistics
                    while IsMouseButtonPressed(1) do
                        -- 记录当前时间
                        ClickCurrentTime = GetRunningTime()
                        -- 计算当前是第几颗子弹
                        BulletIndex = math.ceil((ClickCurrentTime - ClickStartTime == 0 and 1 or (ClickCurrentTime - ClickStartTime) / gunData.interval))
                        if IsDebug then
                            OutputLogMessage("ApplyRecoil ====> " ..
                                "BulletIndex: " ..
                                BulletIndex ..
                                " ClickCurrentTime: " ..
                                ClickCurrentTime ..
                                " ClickStartTime: " .. ClickStartTime .. " #gunData.ballistics: " .. count .. "\n")
                        end
                        -- 当前子弹序号不能超过最大值
                        if BulletIndex > count then break end
                        ApplyRecoil(gunData, BulletIndex)
                    end
                else
                    local gunData = Guns[GunName]
                    -- 计算弹道
                    gunData.ballistics = AccumulateValues(gunData.recoilPattern, RecoilCoefficient)
                    local count = #gunData.ballistics
                    local lastBulletIndex = 1
                    while IsMouseButtonPressed(3) do
                        -- 记录当前时间
                        ClickCurrentTime = GetRunningTime()
                        -- 计算当前是第几颗子弹
                        BulletIndex = math.ceil((ClickCurrentTime - ClickStartTime == 0 and 1 or (ClickCurrentTime - ClickStartTime) / gunData.interval))
                        if IsDebug then
                            OutputLogMessage("ApplyRecoil ====> " ..
                                "BulletIndex: " ..
                                BulletIndex ..
                                " ClickCurrentTime: " ..
                                ClickCurrentTime ..
                                " ClickStartTime: " .. ClickStartTime .. " #gunData.ballistics: " .. count .. "\n")
                        end
                        -- 当前子弹序号不能超过最大值
                        if BulletIndex > count then break end
                        ApplyRecoil(gunData, BulletIndex)
                        if BulletIndex > lastBulletIndex then
                            lastBulletIndex = BulletIndex
                            PressAndReleaseKey("F8")
                        end
                    end
                end
            end
        end
        -- 松开鼠标左键, 恢复动态参数默认值
    elseif event == "MOUSE_BUTTON_RELEASED" and arg == 1 and family == "mouse" then
        ResetConfig()
    end
end
