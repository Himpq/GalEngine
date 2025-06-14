
import os
import sdl2
import sdl2.ext
import pygame
import math
import ctypes
Renderer = None

class screen:
    def __init__(self, width=800, height=600, title="GalEngine SDL2"):
        global Renderer
        sdl2.ext.init()
        
        self.title = title
        self.width = width
        self.height = height

    def init(self):
        global Renderer
        self.window = sdl2.ext.Window(self.title,
                                      size=(self.width, self.height),
                                      flags=sdl2.SDL_WINDOW_FULLSCREEN
                                      )
        self.renderer = sdl2.SDL_CreateRenderer(self.window.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        self.window.show()
        Renderer = self.renderer

    def blitPygame(self, what: pygame.Surface, at):
        raw           = pygame.image.tostring(what, "RGBA", 1)
        width, height = what.get_size()
        sdlSurface    = sdl2.SDL_CreateRGBSurfaceFrom(raw, width, height, 32, width*4, 0x000000ff, 0x0000ff00, 0x00ff0000, 0xff000000)
        texture       = sdl2.SDL_CreateTextureFromSurface(self.renderer, sdlSurface)
        dst           = sdl2.SDL_Rect(int(at[0]), int(at[1]), width, height)

        sdl2.SDL_RenderCopy(self.renderer, texture, None, dst)
        sdl2.SDL_FreeSurface(sdlSurface)
        sdl2.SDL_DestroyTexture(texture)

        self.window.show()

    def blit(self, surface, at):
        """
        surface: SDLSurface 或 (texture, w, h)
        at: (x, y)
        """
        if hasattr(surface, "texture"):
            texture = surface.texture
            w, h = surface.width, surface.height
        elif isinstance(surface, tuple) and len(surface) == 3:
            texture, w, h = surface
        elif isinstance(surface, pygame.Surface):
            surf_str = pygame.image.tostring(surface, "RGBA")
            w, h = surface.get_width(), surface.get_height()
            # 创建SDL_Surface
            sdl_surf = sdl2.SDL_CreateRGBSurfaceWithFormatFrom(
                surf_str, w, h, 32, w * 4, sdl2.SDL_PIXELFORMAT_RGBA32
            )
            texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, sdl_surf)
            sdl2.SDL_FreeSurface(sdl_surf)
        else:
            raise TypeError("blit 只支持 SDLSurface 或 (texture, w, h)")

        dstrect = sdl2.SDL_Rect(int(at[0]), int(at[1]), w, h)
        sdl2.SDL_RenderCopy(self.renderer, texture, None, dstrect)

    def update(self):
        sdl2.SDL_RenderPresent(self.renderer)  # 注释掉
        # sdl2.SDL_UpdateWindowSurface(self.window.window)
    
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    def get_size(self):
        return (self.width, self.height)
    
    # def fill(self, rgb):
    #     color = sdl2.SDL_MapRGB(sdl2.SDL_AllocFormat(sdl2.SDL_PIXELFORMAT_RGBA8888), rgb[0], rgb[1], rgb[2])
    #     rect  = sdl2.SDL_Rect(0, 0, self.get_width(), self.get_height())
    #     sdl2.SDL_SetRenderDrawColor(self.renderer, rgb[0], rgb[1], rgb[2], 255)
    #     sdl2.SDL_RenderFillRect(self.renderer, rect)

    def fill(self, color=(0,0,0,255)):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        sdl2.SDL_SetRenderDrawColor(self.renderer, *color)
        sdl2.SDL_RenderClear(self.renderer)

    def quit(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        self.window.hide()
        sdl2.ext.quit()

    def set_mode(self, size=None, flags=None):
        if size:
            # self.window.size = size
            # sdl2.SDL_SetWindowSize(self.window.window, size[0], size[1])
            self.width, self.height = size

        if flags:
            # Example: handle fullscreen flag from pygame
            if hasattr(pygame, "FULLSCREEN") and (flags & pygame.FULLSCREEN):
                sdl2.SDL_SetWindowFullscreen(self.window.window, sdl2.SDL_WINDOW_FULLSCREEN)
            else:
                sdl2.SDL_SetWindowFullscreen(self.window.window, 0)

class SDLSurface:
    def __init__(self, size, alpha=True, texture=None, orig_surface=None, colorkey=None):
        self.width, self.height = size
        self.renderer           = Renderer
        
        if texture is not None:
            self.texture = texture
        else:
            self.texture = sdl2.SDL_CreateTexture(
                self.renderer,
                sdl2.SDL_PIXELFORMAT_RGBA8888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.width, self.height
            )
        if alpha == pygame.SRCALPHA:
            sdl2.SDL_SetTextureBlendMode(self.texture, sdl2.SDL_BLENDMODE_BLEND)
        self._orig_surface = orig_surface  # 缓存原始surface指针
        self._colorkey = colorkey         # 当前colorkey缓存


    def from_texture(renderer, texture, width, height):
        return SDLSurface(width, height, texture=texture)

    def from_surface(renderer, surf, colorkey=None):
        # 缓存原始surface副本（避免SDL_FreeSurface后失效）
        surf_copy = sdl2.SDL_ConvertSurface(surf, surf.contents.format, 0)
        if colorkey is not None:
            r, g, b = colorkey
            sdl2.SDL_SetColorKey(surf_copy, sdl2.SDL_TRUE, sdl2.SDL_MapRGB(surf_copy.contents.format, r, g, b))
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf_copy)
        sdl2.SDL_SetTextureBlendMode(texture, sdl2.SDL_BLENDMODE_BLEND)  # 关键！
        w, h = surf_copy.contents.w, surf_copy.contents.h
        return SDLSurface((w, h), texture=texture, orig_surface=surf_copy, colorkey=colorkey)

        
    def set_colorkey(self, colorkey):
        """
        设置colorkey（透明色），如colorkey未变则直接返回，否则重新生成texture
        """
        if self._colorkey == colorkey:
            return  # 已经是当前colorkey，无需处理
        if not self._orig_surface:
            return
            # raise RuntimeError("No original surface cached, cannot set colorkey dynamically.")
        # 重新生成texture
        r, g, b = colorkey
        sdl2.SDL_SetColorKey(self._orig_surface, sdl2.SDL_TRUE, sdl2.SDL_MapRGB(self._orig_surface.contents.format, r, g, b))
        # 释放旧texture
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)
        self.texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, self._orig_surface)
        self._colorkey = colorkey

    def set_alpha(self, alpha):
        """设置整体alpha透明度，alpha为0-255或None"""
        sdl2.SDL_SetTextureAlphaMod(self.texture, alpha)

    def fill(self, color):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        sdl2.SDL_SetRenderTarget(self.renderer, self.texture)
        sdl2.SDL_SetRenderDrawColor(self.renderer, *color)
        sdl2.SDL_RenderClear(self.renderer)
        sdl2.SDL_SetRenderTarget(self.renderer, None)

    def blit(self, src_surface, dest, area=None):
        """
        类似 pygame 的 surface.blit
        src_surface: SDLSurface
        dest: (x, y) 或 (x, y, w, h)
        area: (sx, sy, sw, sh) 或 None
        """

        sdl2.SDL_SetTextureBlendMode(self.texture, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_SetTextureBlendMode(src_surface.texture, sdl2.SDL_BLENDMODE_BLEND)

        # 目标区域
        if isinstance(dest, tuple):
            if len(dest) == 2:
                dstrect = sdl2.SDL_Rect(int(dest[0]), int(dest[1]), src_surface.width, src_surface.height)
            elif len(dest) == 4:
                dstrect = sdl2.SDL_Rect(*dest)
            else:
                raise ValueError("dest must be (x, y) or (x, y, w, h)")
        else:
            raise TypeError("dest must be a tuple")

        # 源区域
        srcrect = None
        if area is not None:
            if len(area) == 4:
                srcrect = sdl2.SDL_Rect(*area)
            else:
                raise ValueError("area must be (sx, sy, sw, sh)")

        # 保存当前渲染目标
        prev_target = sdl2.SDL_GetRenderTarget(self.renderer)
        # 切换渲染目标到本 texture
        sdl2.SDL_SetRenderTarget(self.renderer, self.texture)
        # 执行拷贝
        sdl2.SDL_RenderCopy(self.renderer, src_surface.texture, srcrect, dstrect)
        # 恢复渲染目标
        sdl2.SDL_SetRenderTarget(self.renderer, prev_target)

    def free(self):
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)
            self.texture = None
        if self._orig_surface:
            sdl2.SDL_FreeSurface(self._orig_surface)
            self._orig_surface = None

    def __del__(self):
        self.free()
    
    def convert(self):
        return self
    
    def convert_alpha(self):
        return self
    
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    
    def draw_rect(self, color, rect, width=0):
        """
        在本 SDLSurface（即 texture）上绘制矩形
        color: (r,g,b,a)
        rect: (x, y, w, h)
        width: 0 填充，>0 画边框
        """
        # 保存当前渲染目标
        prev_target = sdl2.SDL_GetRenderTarget(self.renderer)
        # 切换渲染目标到本 texture
        sdl2.SDL_SetRenderTarget(self.renderer, self.texture)
        r, g, b, a = [int(i) for i in color]
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, a)
        sdl_rect = sdl2.SDL_Rect(*rect)
        if width == 0:
            sdl2.SDL_RenderFillRect(self.renderer, sdl_rect)
        else:
            for i in range(width):
                border_rect = sdl2.SDL_Rect(
                    int(rect[0]+i), int(rect[1]+i), int(rect[2]-2*i), int(rect[3]-2*i)
                )
                if border_rect.w > 0 and border_rect.h > 0:
                    sdl2.SDL_RenderDrawRect(self.renderer, border_rect)
        # 恢复渲染目标
        sdl2.SDL_SetRenderTarget(self.renderer, prev_target)

    def copy(self):
        return self

class SDLFont:
    def __init__(self, font_path, size):
        if not sdl2.sdlttf.TTF_WasInit():
            sdl2.sdlttf.TTF_Init()
        self.font = sdl2.sdlttf.TTF_OpenFont(font_path.encode('utf-8'), size)
        if not self.font:
            raise RuntimeError(f"Failed to load font: {font_path}")

    def render(self, text, antiatias, color=(255,255,255,255), bgcolor=None):
        """
            渲染文本为surface，color为(r,g,b,a)
            返回SDL_Surface指针
            支持antiatias和bgcolor
        """
        if not text:
            # 返回一个1x1的透明SDLSurface
            surf = sdl2.SDL_CreateRGBSurfaceWithFormat(0, 1, 1, 32, sdl2.SDL_PIXELFORMAT_RGBA32)
            texture = sdl2.SDL_CreateTextureFromSurface(Renderer, surf)
            sdl2.SDL_SetTextureBlendMode(texture, sdl2.SDL_BLENDMODE_BLEND)
            sdl2.SDL_FreeSurface(surf)
            return SDLSurface((1,1), texture=texture)
        # 正常渲染
        sdl_color = sdl2.SDL_Color(*color)

        if bgcolor and (len(bgcolor) == 3 or (len(bgcolor) == 4 and bgcolor[3] != 0)):
            # 有背景色，使用Shaded
            sdl_bgcolor = sdl2.SDL_Color(*bgcolor[:3])
            surf = sdl2.sdlttf.TTF_RenderUTF8_Shaded(self.font, text.encode('utf-8'), sdl_color, sdl_bgcolor)
        else:
            # 无背景色，使用Blended
            surf = sdl2.sdlttf.TTF_RenderUTF8_Blended(self.font, text.encode('utf-8'), sdl_color)

        if not surf:
            raise RuntimeError("Failed to render text", color, bgcolor, self.font, text)
        
        # 将TTF_RenderUTF8_* 返回的 SDL_Surface 指针包装为 SDLSurface
        sdl_surface = SDLSurface.from_surface(Renderer, surf)
        sdl2.SDL_FreeSurface(surf)
        return sdl_surface

    def close(self):
        if self.font:
            sdl2.sdlttf.TTF_CloseFont(self.font)
            self.font = None

    def set_italic(self, italic: bool):
        # SDL_ttf does not support setting italic dynamically.
        # You need to load an italic font file to use italic style.
        # This is a placeholder for compatibility.
        pass

    def set_bold(self, bold: bool):
        if self.font:
            style = sdl2.sdlttf.TTF_GetFontStyle(self.font)
            if bold:
                style |= sdl2.sdlttf.TTF_STYLE_BOLD
            else:
                style &= ~sdl2.sdlttf.TTF_STYLE_BOLD
            sdl2.sdlttf.TTF_SetFontStyle(self.font, style)

    def __del__(self):
        # self.close()
        pass

def SysFont(*arg,**args):
    return SDLFont(os.path.abspath("./source/fonts/MSJH.TTC"), 40)

def scale(surface: SDLSurface, size):
    """
    返回缩放后的新 SDLSurface
    """
    new_w, new_h = size
    # 创建目标 texture
    new_texture = sdl2.SDL_CreateTexture(
        surface.renderer,
        sdl2.SDL_PIXELFORMAT_RGBA8888,
        sdl2.SDL_TEXTUREACCESS_TARGET,
        new_w, new_h
    )
    # 设置渲染目标为新 texture
    prev_target = sdl2.SDL_GetRenderTarget(surface.renderer)
    sdl2.SDL_SetRenderTarget(surface.renderer, new_texture)
    # 清空
    sdl2.SDL_SetRenderDrawColor(surface.renderer, 0, 0, 0, 0)
    sdl2.SDL_RenderClear(surface.renderer)
    # 拉伸绘制
    dstrect = sdl2.SDL_Rect(0, 0, new_w, new_h)
    sdl2.SDL_RenderCopy(surface.renderer, surface.texture, None, dstrect)
    # 恢复渲染目标
    sdl2.SDL_SetRenderTarget(surface.renderer, prev_target)
    return SDLSurface((new_w, new_h), texture=new_texture)

def flip(surface: SDLSurface, xbool, ybool):
    """
    返回翻转后的新 SDLSurface
    """
    new_texture = sdl2.SDL_CreateTexture(
        surface.renderer,
        sdl2.SDL_PIXELFORMAT_RGBA8888,
        sdl2.SDL_TEXTUREACCESS_TARGET,
        surface.width, surface.height
    )
    prev_target = sdl2.SDL_GetRenderTarget(surface.renderer)
    sdl2.SDL_SetRenderTarget(surface.renderer, new_texture)
    sdl2.SDL_SetRenderDrawColor(surface.renderer, 0, 0, 0, 0)
    sdl2.SDL_RenderClear(surface.renderer)
    flip_flag = 0
    if xbool:
        flip_flag |= sdl2.SDL_FLIP_HORIZONTAL
    if ybool:
        flip_flag |= sdl2.SDL_FLIP_VERTICAL
    dstrect = sdl2.SDL_Rect(0, 0, surface.width, surface.height)
    sdl2.SDL_RenderCopyEx(surface.renderer, surface.texture, None, dstrect, 0, None, flip_flag)
    sdl2.SDL_SetRenderTarget(surface.renderer, prev_target)
    return SDLSurface((surface.width, surface.height), texture=new_texture)

def rotate(surface: SDLSurface, angle):
    """
    返回旋转后的新 SDLSurface（角度为度，逆时针）
    """
    # 旋转后尺寸可能变化，这里简单处理为原尺寸
    new_texture = sdl2.SDL_CreateTexture(
        surface.renderer,
        sdl2.SDL_PIXELFORMAT_RGBA8888,
        sdl2.SDL_TEXTUREACCESS_TARGET,
        surface.width, surface.height
    )
    prev_target = sdl2.SDL_GetRenderTarget(surface.renderer)
    sdl2.SDL_SetRenderTarget(surface.renderer, new_texture)
    sdl2.SDL_SetRenderDrawColor(surface.renderer, 0, 0, 0, 0)
    sdl2.SDL_RenderClear(surface.renderer)
    dstrect = sdl2.SDL_Rect(0, 0, surface.width, surface.height)
    sdl2.SDL_RenderCopyEx(surface.renderer, surface.texture, None, dstrect, angle, None, 0)
    sdl2.SDL_SetRenderTarget(surface.renderer, prev_target)
    return SDLSurface((surface.width, surface.height), texture=new_texture)

class draw:
    def rect(target, color, rect, width=0, *arg, **args):
        """
        兼容pygame接口的rect绘制。
        target: SDLSurface 或 renderer
        color: (r,g,b,a)
        rect: (x, y, w, h)
        width: 0 填充，>0 画边框
        """
        # 如果是SDLSurface实例，则在其texture上绘制
        if hasattr(target, "texture") and hasattr(target, "renderer"):
            target.draw_rect(color, rect, width)
        else:
            # 认为是renderer
            r, g, b, a = color
            sdl2.SDL_SetRenderDrawColor(target, r, g, b, a)
            sdl_rect = sdl2.SDL_Rect(*rect)
            if width == 0:
                sdl2.SDL_RenderFillRect(target, sdl_rect)
            else:
                for i in range(width):
                    border_rect = sdl2.SDL_Rect(
                        rect[0]+i, rect[1]+i, rect[2]-2*i, rect[3]-2*i
                    )
                    if border_rect.w > 0 and border_rect.h > 0:
                        sdl2.SDL_RenderDrawRect(target, border_rect)

    
class image:
    def load(path):
        """
        renderer: SDL_Renderer*
        path: 图片路径
        返回: (texture, width, height)
        """
        surf = sdl2.sdlimage.IMG_Load(path.encode('utf-8'))
        if not surf:
            raise RuntimeError(f"Failed to load image: {path}")
        sdl_surface = SDLSurface.from_surface(Renderer, surf)
        sdl2.SDL_FreeSurface(surf)
        return sdl_surface
    
class SDLEvent:
    """
    兼容pygame事件API的SDL事件包装器
    """
    def __init__(self, sdl_event):
        self._event = sdl_event
        self.type = sdl_event.type

        # 键盘事件
        if self.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
            self.key = sdl_event.key.keysym.sym
            self.mod = sdl_event.key.keysym.mod
            self.unicode = getattr(sdl_event.key, "unicode", None)
        # 鼠标移动
        elif self.type == sdl2.SDL_MOUSEMOTION:
            self.pos = (sdl_event.motion.x, sdl_event.motion.y)
            self.rel = (sdl_event.motion.xrel, sdl_event.motion.yrel)
            self.buttons = (
                (sdl_event.motion.state & sdl2.SDL_BUTTON_LMASK) != 0,
                (sdl_event.motion.state & sdl2.SDL_BUTTON_MMASK) != 0,
                (sdl_event.motion.state & sdl2.SDL_BUTTON_RMASK) != 0,
            )
        # 鼠标按键
        elif self.type in (sdl2.SDL_MOUSEBUTTONDOWN, sdl2.SDL_MOUSEBUTTONUP):
            self.pos = (sdl_event.button.x, sdl_event.button.y)
            self.button = sdl_event.button.button
        # 窗口事件
        elif self.type == sdl2.SDL_WINDOWEVENT:
            self.event = sdl_event.window.event
            self.size = (sdl_event.window.data1, sdl_event.window.data2)
        # 文本输入
        elif self.type == sdl2.SDL_TEXTINPUT:
            self.text = sdl_event.text.text.decode("utf-8")
        # 鼠标滚轮
        elif self.type == sdl2.SDL_MOUSEWHEEL:
            self.x = sdl_event.wheel.x
            self.y = sdl_event.wheel.y

    def __getattr__(self, name):
        # 兼容pygame的event.dict
        if name == "dict":
            return self.__dict__
        raise AttributeError(f"'SDLEvent' object has no attribute '{name}'")
