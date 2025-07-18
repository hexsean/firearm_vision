class ConfigManager {
    constructor() {
        this.config = {};
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadConfig();
    }

    setupEventListeners() {
        // 标签页切换
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // 保存按钮
        document.getElementById('saveBtn').addEventListener('click', () => {
            this.saveConfig();
        });

        // 重新加载按钮
        document.getElementById('reloadBtn').addEventListener('click', () => {
            this.loadConfig();
        });

        // 监听输入变化
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('form-control')) {
                this.updateConfigFromForm();
            }
        });
    }

    switchTab(tabName) {
        // 更新标签按钮状态
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // 更新内容显示
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
    }

    async loadConfig() {
        this.showStatus('正在加载配置...', 'loading');
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success) {
                this.config = data.config;
                this.populateForm();
                this.showStatus('配置加载成功', 'success');
            } else {
                this.showStatus(`加载失败: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showStatus(`加载失败: ${error.message}`, 'error');
        }
    }

    async saveConfig() {
        this.showStatus('正在保存配置...', 'loading');
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showStatus('配置保存成功', 'success');
            } else {
                this.showStatus(`保存失败: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showStatus(`保存失败: ${error.message}`, 'error');
        }
    }

    populateForm() {
        // 基础设置
        this.setInputValue('lua_config_path', this.config.lua_config_path);
        this.setInputValue('is_debug', this.config.is_debug, 'checkbox');
        this.setInputValue('target_fps', this.config.target_fps);
        this.setInputValue('weapon_altitude', this.config.weapon_altitude);
        this.setInputValue('vertical_sensitivity_magnification', this.config.vertical_sensitivity_magnification);

        // 屏幕设置
        if (this.config.screen_resolution) {
            this.setInputValue('screen_width', this.config.screen_resolution[0]);
            this.setInputValue('screen_height', this.config.screen_resolution[1]);
        }

        if (this.config.overlay_position) {
            this.setInputValue('overlay_x', this.config.overlay_position[0]);
            this.setInputValue('overlay_y', this.config.overlay_position[1]);
        }

        // 截图区域
        this.populateScreenshotAreas();

        // 武器配置
        this.populateFirearms();

        // 配件系数
        this.populateAccessories();

        // 索引位置
        this.populateIndex();
    }

    populateScreenshotAreas() {
        const areas = [
            'weapon_screenshot_area', 'muzzle_screenshot_area',
            'grip_screenshot_area', 'butt_screenshot_area', 'sight_screenshot_area',
            'muzzle_screenshot_area2', 'grip_screenshot_area2',
            'butt_screenshot_area2', 'sight_screenshot_area2'
        ];

        areas.forEach(areaName => {
            const areaData = this.config[areaName];
            if (areaData) {
                const areaElement = document.querySelector(`[data-area="${areaName}"]`);
                if (areaElement) {
                    ['left', 'top', 'width', 'height'].forEach(field => {
                        const input = areaElement.querySelector(`[data-field="${field}"]`);
                        if (input) {
                            input.value = areaData[field] || 0;
                        }
                    });
                }
            }
        });
    }

    populateFirearms() {
        const firearmsContainer = document.getElementById('firearms-list');
        firearmsContainer.innerHTML = '';

        if (this.config.firearms) {
            Object.keys(this.config.firearms).forEach(weaponName => {
                const weaponData = this.config.firearms[weaponName];
                const weaponElement = this.createFirearmElement(weaponName, weaponData);
                firearmsContainer.appendChild(weaponElement);
            });
        }
    }

    createFirearmElement(weaponName, weaponData) {
        const div = document.createElement('div');
        div.className = 'firearm-config';
        div.innerHTML = `
            <h3>${weaponName.toUpperCase()}</h3>
            <div class="form-group">
                <label>识别置信度阈值:</label>
                <input type="number" step="0.01" min="0" max="1" 
                       class="form-control firearm-threshold" 
                       data-weapon="${weaponName}"
                       value="${weaponData.recognition_confidence_threshold || 0.4}">
            </div>
            <div class="form-group">
                <label>系数列表:</label>
                <div class="coefficient-list">
                    <div class="coefficient-item">
                        <label>基础:</label>
                        <input type="number" step="0.01" class="form-control firearm-coeff" 
                               data-weapon="${weaponName}" data-index="0"
                               value="${weaponData.coefficient_list[0] || 1.0}">
                    </div>
                    <div class="coefficient-item">
                        <label>站立:</label>
                        <input type="number" step="0.01" class="form-control firearm-coeff" 
                               data-weapon="${weaponName}" data-index="1"
                               value="${weaponData.coefficient_list[1] || 1.0}">
                    </div>
                    <div class="coefficient-item">
                        <label>蹲下:</label>
                        <input type="number" step="0.01" class="form-control firearm-coeff" 
                               data-weapon="${weaponName}" data-index="2"
                               value="${weaponData.coefficient_list[2] || 0.78}">
                    </div>
                    <div class="coefficient-item">
                        <label>趴下:</label>
                        <input type="number" step="0.01" class="form-control firearm-coeff" 
                               data-weapon="${weaponName}" data-index="3"
                               value="${weaponData.coefficient_list[3] || 0.545}">
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    populateAccessories() {
        const accessoriesContainer = document.getElementById('accessories-config');
        accessoriesContainer.innerHTML = '';

        if (this.config.firearms_accessories_list) {
            const accessories = this.config.firearms_accessories_list;
            
            // 默认枪口系数
            const defMuzzleDiv = document.createElement('div');
            defMuzzleDiv.className = 'form-group';
            defMuzzleDiv.innerHTML = `
                <label>默认枪口系数:</label>
                <input type="number" step="0.001" class="form-control" 
                       id="def_muzzle" value="${accessories.def_muzzle || 1.265}">
            `;
            accessoriesContainer.appendChild(defMuzzleDiv);

            // 各类配件
            const accessoryTypes = [
                { key: 'muzzle_list', name: '枪口配件' },
                { key: 'grip_list', name: '握把配件' },
                { key: 'butt_list', name: '枪托配件' },
                { key: 'sight_list', name: '瞄具配件' }
            ];

            accessoryTypes.forEach(type => {
                if (accessories[type.key]) {
                    const section = this.createAccessorySection(type.name, type.key, accessories[type.key]);
                    accessoriesContainer.appendChild(section);
                }
            });
        }
    }

    createAccessorySection(name, key, items) {
        const section = document.createElement('div');
        section.className = 'accessories-section';
        
        let itemsHtml = '';
        Object.keys(items).forEach(itemName => {
            itemsHtml += `
                <div class="form-group">
                    <label>${itemName}:</label>
                    <input type="number" step="0.001" class="form-control accessory-item" 
                           data-type="${key}" data-name="${itemName}"
                           value="${items[itemName]}">
                </div>
            `;
        });

        section.innerHTML = `
            <h3>${name}</h3>
            <div class="accessory-grid">
                ${itemsHtml}
            </div>
        `;
        
        return section;
    }

    populateIndex() {
        const indexContainer = document.getElementById('index-config');
        indexContainer.innerHTML = '';

        if (this.config.index) {
            const indexDiv = document.createElement('div');
            indexDiv.className = 'index-grid';
            
            Object.keys(this.config.index).forEach(indexName => {
                const indexData = this.config.index[indexName];
                const itemDiv = this.createIndexItem(indexName, indexData);
                indexDiv.appendChild(itemDiv);
            });
            
            indexContainer.appendChild(indexDiv);
        }
    }

    createIndexItem(name, data) {
        const div = document.createElement('div');
        div.className = 'index-item';
        
        let inputsHtml = '';
        if (Array.isArray(data)) {
            data.forEach((value, index) => {
                const label = index === 0 ? 'X' : index === 1 ? 'Y' : `值${index + 1}`;
                inputsHtml += `
                    <div class="coordinate-input">
                        <label>${label}:</label>
                        <input type="number" class="form-control index-coord" 
                               data-index-name="${name}" data-coord-index="${index}"
                               value="${value}">
                    </div>
                `;
            });
        }

        div.innerHTML = `
            <h4>${name}</h4>
            ${inputsHtml}
        `;
        
        return div;
    }

    updateConfigFromForm() {
        // 基础设置
        this.config.lua_config_path = this.getInputValue('lua_config_path');
        this.config.is_debug = this.getInputValue('is_debug', 'checkbox');
        this.config.target_fps = parseInt(this.getInputValue('target_fps')) || 15;
        this.config.weapon_altitude = parseInt(this.getInputValue('weapon_altitude')) || 75;
        this.config.vertical_sensitivity_magnification = parseFloat(this.getInputValue('vertical_sensitivity_magnification')) || 1.0;

        // 屏幕设置
        const screenWidth = parseInt(this.getInputValue('screen_width'));
        const screenHeight = parseInt(this.getInputValue('screen_height'));
        if (screenWidth && screenHeight) {
            this.config.screen_resolution = [screenWidth, screenHeight];
        }

        const overlayX = parseInt(this.getInputValue('overlay_x'));
        const overlayY = parseInt(this.getInputValue('overlay_y'));
        if (!isNaN(overlayX) && !isNaN(overlayY)) {
            this.config.overlay_position = [overlayX, overlayY];
        }

        // 更新截图区域
        this.updateScreenshotAreas();

        // 更新武器配置
        this.updateFirearms();

        // 更新配件系数
        this.updateAccessories();

        // 更新索引位置
        this.updateIndex();
    }

    updateScreenshotAreas() {
        document.querySelectorAll('[data-area]').forEach(areaElement => {
            const areaName = areaElement.dataset.area;
            if (!this.config[areaName]) {
                this.config[areaName] = {};
            }

            ['left', 'top', 'width', 'height'].forEach(field => {
                const input = areaElement.querySelector(`[data-field="${field}"]`);
                if (input && input.value) {
                    this.config[areaName][field] = parseInt(input.value) || 0;
                }
            });
        });
    }

    updateFirearms() {
        // 更新武器阈值
        document.querySelectorAll('.firearm-threshold').forEach(input => {
            const weaponName = input.dataset.weapon;
            if (this.config.firearms && this.config.firearms[weaponName]) {
                this.config.firearms[weaponName].recognition_confidence_threshold = parseFloat(input.value) || 0.4;
            }
        });

        // 更新武器系数
        document.querySelectorAll('.firearm-coeff').forEach(input => {
            const weaponName = input.dataset.weapon;
            const index = parseInt(input.dataset.index);
            if (this.config.firearms && this.config.firearms[weaponName]) {
                if (!this.config.firearms[weaponName].coefficient_list) {
                    this.config.firearms[weaponName].coefficient_list = [1.0, 1.0, 0.78, 0.545];
                }
                this.config.firearms[weaponName].coefficient_list[index] = parseFloat(input.value) || 1.0;
            }
        });
    }

    updateAccessories() {
        if (!this.config.firearms_accessories_list) {
            this.config.firearms_accessories_list = {};
        }

        // 默认枪口系数
        const defMuzzleInput = document.getElementById('def_muzzle');
        if (defMuzzleInput) {
            this.config.firearms_accessories_list.def_muzzle = parseFloat(defMuzzleInput.value) || 1.265;
        }

        // 配件系数
        document.querySelectorAll('.accessory-item').forEach(input => {
            const type = input.dataset.type;
            const name = input.dataset.name;
            if (!this.config.firearms_accessories_list[type]) {
                this.config.firearms_accessories_list[type] = {};
            }
            this.config.firearms_accessories_list[type][name] = parseFloat(input.value) || 1.0;
        });
    }

    updateIndex() {
        if (!this.config.index) {
            this.config.index = {};
        }

        document.querySelectorAll('.index-coord').forEach(input => {
            const indexName = input.dataset.indexName;
            const coordIndex = parseInt(input.dataset.coordIndex);
            
            if (!this.config.index[indexName]) {
                this.config.index[indexName] = [];
            }
            
            this.config.index[indexName][coordIndex] = parseInt(input.value) || 0;
        });
    }

    setInputValue(id, value, type = 'text') {
        const element = document.getElementById(id);
        if (element) {
            if (type === 'checkbox') {
                element.checked = Boolean(value);
            } else {
                element.value = value || '';
            }
        }
    }

    getInputValue(id, type = 'text') {
        const element = document.getElementById(id);
        if (element) {
            return type === 'checkbox' ? element.checked : element.value;
        }
        return '';
    }

    showStatus(message, type) {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = `status ${type}`;
        
        if (type === 'success' || type === 'error') {
            setTimeout(() => {
                statusElement.textContent = '';
                statusElement.className = 'status';
            }, 3000);
        }
    }
}

// 初始化配置管理器
document.addEventListener('DOMContentLoaded', () => {
    new ConfigManager();
});
