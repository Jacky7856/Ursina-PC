from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter.messagebox import *
import os, random, json

# 初始化Tkinter
root = tk.Tk()
root.withdraw()  # 隐藏主Tkinter窗口

# 初始化Ursina
app = Ursina()

# 方块材质配置
textures = [
    load_texture('grass.png'),   # 确保这些图片存在于项目目录中
    load_texture('bricks.png'),
    load_texture('stone.png'),
    load_texture('wood.png'),
    load_texture('wen.png')
]

class Block(Button):
    def __init__(self, position=(0,0,0), texture_index=0):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=textures[texture_index],
            color=color.color(random.uniform(0.9, 1), 0, random.uniform(0.9, 1)),
            highlight_color=color.lime,
            collider='box',
            scale=1
        )
        self.texture_index = texture_index

blocks = []
current_block_type = 0

# 世界初始化函数
def init_world():
    global blocks
    # 清除现有方块
    for block in blocks.copy():
        destroy(block)
    blocks.clear()
    
    # 生成新世界（20x20地面 + 5层地下）
    for x in range(20):
        for z in range(20):
            # 地面层（草地方块）
            blocks.append(Block(position=(x,0,z), texture_index=0))
            # 地下层（石砖）
            for y in range(1, 6):
                blocks.append(Block(position=(x,-y,z), texture_index=2))

# 改进后的保存函数
def save_world(filename):
    try:
        if not filename.endswith('.json'):
            filename += '.json'
            
        save_data = []
        for block in blocks:
            save_data.append({
                'position': [block.x, block.y, block.z],
                'texture_index': block.texture_index
            })
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        showinfo("保存成功", f"世界已保存至 {os.path.abspath(filename)}")
        return True
    except Exception as e:
        showerror("保存失败", f"错误信息：{str(e)}")
        return False

# 改进后的加载函数
def load_world(filename):
    global blocks
    try:
        if not filename.endswith('.json'):
            filename += '.json'
        if not os.path.exists(filename):
            showwarning("文件不存在", "将创建新世界")
            init_world()
            return False
        
        # 清除旧方块
        for block in blocks.copy():
            destroy(block)
        blocks.clear()
        # 加载新数据
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
            
        for block_data in loaded_data:
            pos = block_data['position']
            new_block = Block(
                position=tuple(pos),  # 确保位置是元组
                texture_index=block_data['texture_index']
            )
            blocks.append(new_block)
        showinfo("加载成功", f"已从 {filename} 加载世界")
        return True
    except Exception as e:
        showerror("加载失败", f"错误信息：{str(e)}\n已创建新世界")
        init_world()
        return False
# 玩家控制器
player = FirstPersonController(
    mouse_sensitivity=Vec2(50, 50),
    jump_height=1.2,
    height=1.6
)
# 游戏逻辑更新
def update():
    # 玩家坠落保护
    if player.y < -100:
        player.position = (10, 100, 10)
    global current_block_type
    # 方块类型切换
    if held_keys['1']: current_block_type = 0
    if held_keys['2']: current_block_type = 1
    if held_keys['3']: current_block_type = 2
    if held_keys['4']: current_block_type = 3
    if held_keys['5']: current_block_type = 4
def input(key):
    global blocks, current_block_type
    # 方块放置
    if key == 'left mouse down':
        hit = raycast(camera.world_position, camera.forward, distance=5)
        if hit.hit:
            new_pos = hit.entity.position + hit.normal
            # 防止在玩家附近放置
            if distance(player.position, new_pos) > 2:
                blocks.append(Block(
                    position=new_pos,
                    texture_index=current_block_type
                ))
    # 方块破坏
    if key == 'right mouse down':
        hit = raycast(camera.world_position, camera.forward, distance=5)
        if hit.hit:
            if hit.entity in blocks:
                blocks.remove(hit.entity)
                destroy(hit.entity)
    
    # 保存并退出
    if key == 'escape':
        filename = askstring("保存世界", "输入存档名称：")
        if filename:
            if filename == 'help(123)':
                showinfo("帮助", "输入存档名称，不需要扩展名\n将自动保存为.json文件")
            elif save_world(filename):
                application.quit()
        else:
            showinfo("提示", "已取消保存")
# 启动界面
def main_menu():
    menu = tk.Tk()
    menu.title("SanGame - 主菜单")
    
    def new_game():
        init_world()
        menu.destroy()
        app.run()
    
    def load_game():
        filename = askstring("加载世界", "输入存档名称：")
        if filename:
            if load_world(filename):
                menu.destroy()
                app.run()
        else:
            showinfo("提示", "已取消加载")
    
    tk.Button(menu, text="新建世界", command=new_game, width=20).pack(pady=5)
    tk.Button(menu, text="加载世界", command=load_game, width=20).pack(pady=5)
    tk.Button(menu, text="退出游戏", command=menu.destroy, width=20).pack(pady=5) 
    menu.mainloop()
if __name__ == '__main__':
    main_menu()