import logging

import sys

from ..game import Mode
from .. import dmd
from ..dmd import TransitionLayer
from ..dmd import Transition
from ..dmd import HDTextLayer
from ..dmd import HDFont
from ..dmd import RandomizedLayer
from ..dmd import AnimatedLayer
from ..dmd import ScriptlessLayer
from procgame.yaml_helper import value_for_key
import yaml


class DMDHelper(Mode):
    """A mode that displays a message to the player on the DMD"""
    msgfont = None

    def __init__(self, game):
        super(DMDHelper, self).__init__(game=game, priority=12)
        self.logger = logging.getLogger('dmdhelper')
        self.timer_name = 'message_display_ended'
        self.msgfont = self.game.fonts['default']

        self.game.status_font_name = 'status_font'
        self.prev_layer = None

        if ('status_font_style' in self.game.fontstyles):
            self.game.status_font_style = 'status_font_style'
        else:
            self.game.status_font_style = None

        if ('status_bg' not in self.game.animations or self.game.animations['status_bg'] is None):
            t2 = dmd.SolidLayer(int(self.game.dmd_width * .8), int(self.game.dmd_height * .5), (255, 196, 0, 255))
            self.game.animations['status_bg'] = dmd.GroupedLayer(int(self.game.dmd_width * .8),
                                                                 int(self.game.dmd_height * .5), [t2])  # ,t1
            self.game.animations['status_bg'].set_target_position(int(self.game.dmd_width * .1),
                                                                  int(self.game.dmd_height * .25))

        pass

    def msg_over(self):
        self.layer = None

    def genMsgFrame(self, msg, background_layer=None, font_style=None, font_key=None, opaque=False, flashing=False):
        if (font_style is None):
            if 'default' in self.game.fontstyles:
                font_style = self.game.fontstyles['default']
            else:
                font_style = dmd.HDFontStyle()
        elif (isinstance(font_style, basestring)):
            font_style = self.game.fontstyles[font_style]

        if (font_key is None):
            font = self.msgfont
        elif (type(font_key) is str):
            font = self.game.fonts[font_key]
        else:
            font = font_key

        if (isinstance(msg, list)):
            num_lines = len(msg)
            t_layers = []
            i = 1
            for line in msg:
                if (line != ""):
                    if type(line) is int:
                        line = str(line)
                    else:
                        line = line.decode('ascii', 'ignore')
                    tL = dmd.HDTextLayer(self.game.dmd.width / 2, self.game.dmd.height * i / (num_lines + 1), font,
                                         "center", vert_justify="center", opaque=False, width=self.game.dmd.width,
                                         height=100, line_color=font_style.line_color, line_width=font_style.line_width,
                                         interior_color=font_style.interior_color,
                                         fill_color=font_style.fill_color).set_text(line, blink_frames=flashing)
                    t_layers.append(tL)
                i = i + 1
            t = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, t_layers)
        else:
            if (msg is not None):
                if type(msg) is int:
                    msg = str(msg)
                else:
                    msg = msg.decode('ascii', 'ignore')
            t = dmd.HDTextLayer(self.game.dmd.width / 2, self.game.dmd.height / 2, font, "center",
                                vert_justify="center", opaque=False, width=self.game.dmd.width, height=100,
                                line_color=font_style.line_color, line_width=font_style.line_width,
                                interior_color=font_style.interior_color, fill_color=font_style.fill_color).set_text(
                msg, blink_frames=flashing)

        if (background_layer is None):
            t.opaque = opaque
            return t
        else:
            t.opaque = opaque
            t.composite_op = "blacksrc"
            # t = dmd.HDTextLayer(self.game.dmd.width/2, self.game.dmd.height/4, self.msgfont, "center", opaque=False).set_text(msg)
            # t = TransitionLayer(layerA=None, layerB=txt, transitionType=Transition.TYPE_CROSSFADE, transitionParameter=None)

            if (isinstance(background_layer, list)):
                lAnimations = [self.game.animations[animation_key] for animation_key in background_layer]
                for each_anim in lAnimations:
                    each_anim.reset()
                lAnimations.append(t)
                # lAnimations[0].opaque=True
                gl = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, lAnimations)
            else:
                # self.game.animations[background_layer].opaque=True
                self.game.animations[background_layer].reset()
                gl = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
                                      [self.game.animations[background_layer], t])
            gl.opaque = opaque
            return gl

    """ called when the machine is reset, before we dump the mode from the queue """

    def reset(self):
        self.layer = None
        self.cancel_delayed(name=self.timer_name)

    def showMessage(self, msg, background_layer=None, font_style=None, opaque=False, duration=2.0, font_key=None,
                    flashing=False):
        self.layer = self.genMsgFrame(msg, background_layer=background_layer, font_style=font_style, opaque=opaque,
                                      font_key=font_key, flashing=flashing)
        self.message = msg

        # cancel any old outstanding timers
        self.cancel_delayed(name=self.timer_name)

        # create a new timer
        self.delay(name=self.timer_name,
                   event_type=None,
                   delay=duration,
                   handler=self.msg_over)

    def __parse_relative_num(self, yaml_struct, key, relative_to, default, relative_match=None):
        """ parses the key from the given yaml_struct and computes
            its value relative to the value passed for relative_to

            if a positive int is specified, the value is taken as-is
            if a negative int is specified, the value is taken as offset from the relative value
            if a float is specified the value is taken as a percentage of the relative value
            if a string value matching the key is specified, the relative value is returned
                (equiv to specifying 1.0 as 100%)
        """
        if (relative_match is None):
            relative_match = key

        tmp = value_for_key(yaml_struct, key, default)
        if (isinstance(tmp, int)):
            # offset values -- use the values as given unless negative!
            if (tmp < 0):
                tmp = relative_to + tmp
            pass
        elif (isinstance(tmp, float)):
            # percentage values - set to appropriate percentage of 'relative_to' value
            tmp = relative_to * tmp
        elif (isinstance(tmp, basestring) and (tmp == relative_match)):
            tmp = relative_to
        return tmp

    def __parse_position_data(self, yaml_struct, for_text=False):
        """ returns a tuple of x/y values for placement or x/y/horiz_justify/vert_justify
            if for_text is True; expects data to be found in yaml_struct.
            Fallback values are different for_text (centered) vs. other types of
            content (top left -- 0,0)
        """

        if (for_text):
            fallback = 0.5
        else:
            fallback = int(0)

        x = self.__parse_relative_num(yaml_struct, key='x', relative_to=self.game.dmd.width, default=fallback,
                                      relative_match="width")
        y = self.__parse_relative_num(yaml_struct, key='y', relative_to=self.game.dmd.height, default=fallback,
                                      relative_match="height")

        if (for_text):
            vj = value_for_key(yaml_struct, 'v_justify', "center")
            hj = value_for_key(yaml_struct, 'h_justify', "center")
            return (x, y, hj, vj)
        return (x, y)

    def parse_font_data(self, yaml_struct, required=True):
        """ returns a Font and FontStyle as loaded from a yaml based descriptor of
            Font and FontStyle information. """
        # get font
        fname = value_for_key(yaml_struct, 'font', value_for_key(yaml_struct, 'Font'))
        if (fname is None):
            if (required):
                raise ValueError, "Cannot find required Font tag in yaml segment [%s]" % (yaml_struct)
            else:
                f = None
        else:
            if (fname not in self.game.fonts):
                self.logger.error(
                    "yaml refers to a font '%s' that does not exist.  Please check the assetList to ensure this font is present" % fname)

            # the assetManager will take care of providing a default font even if the above doesn't work
            f = self.game.fonts[fname]

        # get font style
        font_style = value_for_key(yaml_struct, 'font_style', value_for_key(yaml_struct, 'FontStyle'))
        if (isinstance(font_style, dict)):
            # dive deeper into this struct, making a new font_style on the fly for the user
            ic = value_for_key(font_style, 'interior_color')
            lc = value_for_key(font_style, 'line_color')
            lw = value_for_key(font_style, 'line_width')
            # k = value_for_key(font_style, 'key')
            font_style = dmd.HDFontStyle(interior_color=ic,
                                         line_width=lw,
                                         line_color=lc)
            # self.fontstyles[k] = font_style

        elif (isinstance(font_style, basestring)):
            font_style = self.game.fontstyles[font_style]
        else:
            # no font style specified or value is none
            font_style = None

        return f, font_style

    def generateTextLayerFromYaml(self, yaml_struct):
        """ parses a text descriptor format yaml and generates a text layer to be filled with text via set_text()
              For now, the score_display.yaml example(s) should suffice; better documentation forthcoming
        """
        enabled = value_for_key(yaml_struct, 'enabled', True)
        if (not enabled):
            return None

        (f, font_style) = self.parse_font_data(yaml_struct)
        (x, y, hj, vj) = self.__parse_position_data(yaml_struct, for_text=True)
        opaque = value_for_key(yaml_struct, 'opaque', False)

        interior = value_for_key(yaml_struct, 'interior', None)

        # create the layer -- it matters if we have an HD font or not...
        if (isinstance(f, HDFont)):
            if (interior is not None):
                tL = dmd.AnimatedHDTextLayer(x=x, y=y,
                                             font=f, justify=hj, vert_justify=vj,
                                             fill_anim=self.game.animations[interior],
                                             width=self.game.dmd.width, height=self.game.dmd.height,
                                             line_color=font_style.line_color, line_width=font_style.line_width)

            else:
                tL = dmd.HDTextLayer(x=x, y=y, font=f, justify=hj, vert_justify=vj, opaque=opaque, width=None,
                                     height=None)

            tL.style = font_style
        else:
            tL = dmd.TextLayer(x=x, y=y, font=f, justify=hj, opaque=opaque, width=None, height=None, fill_color=None)

        tL.enabled = value_for_key(yaml_struct, "visible", True)

        return tL

    def genLayerFromYAML(self, yamlStruct):
        """ a helper that parses the 'attract sequence' format -- an augmented version
            of the yaml serialized layer format, however also includes coordination
            of lampshows and sound playback """

        duration = None
        lampshow = None
        sound = None
        lyrTmp = None
        name = None
        v = None
        try:
            if ('HighScores' in yamlStruct):
                v = yamlStruct['HighScores']

                duration = value_for_key(v, 'duration', 2.0)
                lampshow = value_for_key(v, 'lampshow')
                sound = value_for_key(v, 'sound')

                fields = value_for_key(v, 'Order')
                (fnt, font_style) = self.parse_font_data(v, required=False)

                background = value_for_key(v, 'Animation', value_for_key(v, 'Animation'))

                # lyrTmp = dmd.ScriptlessLayer(self.game.dmd.width,self.game.dmd.height)
                # entry_ct = len(self.game.get_highscore_data())
                # for rec in self.game.get_highscore_data():
                #     if fields is not None:
                #         records = [rec[f] for f in fields]
                #     else:
                #         records = [rec['category'], rec['player'], rec['score']]
                #     lT = self.genMsgFrame(records, background, font_key=fnt, font_style=font_style)

                #     lyrTmp.append(lT, duration)

                # duration = entry_ct*duration
                lyrTmp = dmd.ScoresLayer(self.game, fields, fnt, font_style, background, duration)
                duration = lyrTmp.get_duration()

            elif ('LastScores' in yamlStruct):
                v = yamlStruct['LastScores']

                duration = value_for_key(v, 'duration', 2.0)
                lampshow = value_for_key(v, 'lampshow')
                sound = value_for_key(v, 'sound')

                (fnt, font_style) = self.parse_font_data(v, required=False)

                background = value_for_key(v, 'Animation', value_for_key(v, 'Animation'))

                multiple_screens = value_for_key(v, 'multiple_screens', False)

                lyrTmp = dmd.LastScoresLayer(self.game, multiple_screens, fnt, font_style, background, duration)

                duration = lyrTmp.get_duration()
            elif ('RandomText' in yamlStruct):
                v = yamlStruct['RandomText']
                (fnt, font_style) = self.parse_font_data(v, required=False)
                randomText = value_for_key(v, 'TextOptions', exception_on_miss=True)
                headerText = value_for_key(v, 'Header', None)
                duration = value_for_key(v, 'duration')

                rndmLayers = []
                for line in randomText:
                    selectedRandomText = line['Text']
                    if (type(selectedRandomText) is list):
                        completeText = selectedRandomText
                    else:
                        completeText = [selectedRandomText]

                    if (headerText is not None):
                        completeText[:0] = [headerText]  # prepend the header text entry at the start of the list

                    rndmLayers.append(self.genMsgFrame(completeText, value_for_key(v, 'Animation'), font_key=fnt,
                                                       font_style=font_style))

                if (len(rndmLayers) > 0):
                    lyrTmp = RandomizedLayer(layers=rndmLayers)

                # Apply any transformations
                #lyrTmp = self.apply_transforms(lyrTmp, v)
            else:
                lyrTmp = self.generateLayerFromYaml(yamlStruct)  # not sure what this is, let the other method parse it
                v = yamlStruct[
                    yamlStruct.keys()[0]]  # but we reach in and grab it to pull duration, lampshow and sound.

                duration = value_for_key(v, 'duration', None)

                name = value_for_key(v, 'Name', None)

            if (v is not None):
                lampshow = value_for_key(v, 'lampshow')
                sound = value_for_key(v, 'sound')

        except Exception, e:
            current_tag = None
            if (yamlStruct is not None and len(yamlStruct.keys()) > 0):
                current_tag = yamlStruct.keys()[0]
            self.logger.critical(
                "YAML processing failure occured within tag '%s' of yaml section: \n'%s'" % (current_tag, yamlStruct))
            raise e

        return (lyrTmp, duration, lampshow, sound, name)

    def apply_transforms(self, layer, yaml_dict, x=0, y=0):

        trans_applied = False

        # Apply Rotation
        if not isinstance(layer, dmd.HDTextLayer):
            if (value_for_key(yaml_dict, 'rotate_layer') is not None):
                (layer, trans_applied) = self.apply_rotation(layer, yaml_dict['rotate_layer'])

        # Apply Zoom
        if (value_for_key(yaml_dict, 'zoom_layer') is not None):
            (layer, trans_applied) = self.apply_zoom(layer, yaml_dict['zoom_layer'])

        if (value_for_key(yaml_dict, 'fade') is not None):
            (layer, trans_applied) = self.apply_fade(layer, yaml_dict['fade'])

        if (value_for_key(yaml_dict, 'move_layer') is not None):
            layer = self.apply_move(layer, yaml_dict['move_layer'])

        return (layer, trans_applied)

    def apply_zoom(self, layer, zoom_dict):
        """ Applys zoom to a layer from zoom_dict values """

        enabled = value_for_key(zoom_dict, 'enabled', False)
        if not enabled:
            return (layer, False)

        hold = value_for_key(zoom_dict, 'hold', False)
        start = value_for_key(zoom_dict, 'scale_start', 0.1)
        stop = value_for_key(zoom_dict, 'scale_stop', 1.0)
        total_zooms = value_for_key(zoom_dict, 'total_zooms', 30)
        frames_per_zoom = value_for_key(zoom_dict, 'frames_per_zoom', 1)

        # Get the highest scale used
        scale = 0
        if start > stop:
            scale = start
        else:
            scale = stop

        w = 0
        h = 0
        if isinstance(layer, dmd.MovieLayer):
            return (dmd.GroupedLayer(layer.frame.width * scale, layer.frame.height * scale,
                                     [dmd.ZoomingLayer(layer, hold, frames_per_zoom, start, stop, total_zooms)]), True)
        else:
            return (dmd.GroupedLayer(layer.frames[0].width * scale, layer.frames[0].height * scale,
                                     [dmd.ZoomingLayer(layer, hold, frames_per_zoom, start, stop, total_zooms)]), True)

    def apply_rotation(self, layer, rotate_dict, pos_x=0, pos_y=0):

        enabled = value_for_key(rotate_dict, 'enabled', False)
        if not enabled:
            return (layer, False)

        x = value_for_key(rotate_dict, 'x', 0)
        y = value_for_key(rotate_dict, 'y', 0)
        rotation_update = value_for_key(rotate_dict, 'rotation_update', 10)

        w = 0
        h = 0
        if isinstance(layer, dmd.GroupedLayer):
            w = layer.width
            h = layer.height
            # group = dmd.GroupedLayer(w, h, [layer])
            group = dmd.GroupedLayer(w, h,
                                     [dmd.RotationLayer(x, y, rotation_update, layer)])
        elif isinstance(layer, dmd.MovieLayer):
            w = layer.movie.width
            h = layer.movie.height
            group = dmd.GroupedLayer(w, h, [layer])
            group = dmd.GroupedLayer(w, h,
                                     [dmd.RotationLayer(x, y, rotation_update, group)])
        else:
            if hasattr(layer, 'width'):
                w = layer.width
                h = layer.height
            else:
                w = layer.frames[0].width
                h = layer.frames[0].height

            group = dmd.GroupedLayer(w, h, [layer])
            group = dmd.GroupedLayer(w, h, [dmd.RotationLayer(x, y, rotation_update, group)])

        return group, True

    def apply_move(self, layer, move_dict):

        enabled = value_for_key(move_dict, 'enabled', False)
        if not enabled:
            return layer

        sx = value_for_key(move_dict, 'start_x', 0)
        sy = value_for_key(move_dict, 'start_y', 0)
        tx = value_for_key(move_dict, 'target_x', 0)
        ty = value_for_key(move_dict, 'target_y', 0)
        frames = value_for_key(move_dict, 'frames', 15)
        loop = value_for_key(move_dict, 'loop', False)

        # Needs all all this to stop cropping of images?
        #
        # group = None
        # if isinstance(layer, tuple):
        #     layer = layer[0][0][0]
        #     if isinstance(layer, tuple):
        #         layer = layer[0][0]
        #         if isinstance(layer, tuple):
        #             layer = layer[0]
        #
        #     group = dmd.GroupedLayer(layer.width, layer.height, [layer])
        #
        # elif isinstance(layer, dmd.layers.GroupedLayer):
        #     group = layer
        # elif isinstance(layer, HDTextLayer):
        #     group = dmd.GroupedLayer(layer.width, layer.height, [layer])
        # elif isinstance(layer, dmd.ScaledLayer):
        #     group = dmd.GroupedLayer(layer.width, layer.height, [layer])
        # elif isinstance(layer, dmd.FrameLayer) or isinstance(layer, dmd.HDTextLayer):
        #     group = dmd.GroupedLayer(layer.frame.width, layer.frame.height, [layer])
        # else:
        #     group = dmd.GroupedLayer(layer.get_width(), layer.get_height(), [layer])

        return dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, [dmd.moveLayer(layer, sx, sy, tx, ty, frames, loop=loop)])

    def apply_fade(self, layer, fade_dict):
        """ 
        Applys a fade transition. Goes from a None layer to the layer, vice versa, depending on In/Out.
        :param layer: The layer to apply a fade to
        :param fade_dict: Fade fict values. param - framecount
        :return: A transition layer or original layer
        """""

        param = value_for_key(fade_dict, 'param', 'off')
        sl = ScriptlessLayer(self.game.dmd.width, self.game.dmd.height)
        if param == 'off':
            return (layer, False)
        else:
            frame_count = value_for_key(fade_dict, 'frame_count', 30)
            # if True:
            #     sl.append(dmd.TransitionLayer(None, layer, Transition.TYPE_FADE, 'in', frame_count), 1.0 * frame_count)
            #     sl.append(dmd.TransitionLayer(layer, None, Transition.TYPE_FADE, 'out', frame_count), 1.0 * frame_count)
            #     return (dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, [sl]), True)
            # else:
            if param == 'out':
                trans = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
                                         [dmd.TransitionLayer(layer, None, Transition.TYPE_FADE, param, frame_count)])
                return (trans, True)
            elif param == 'in':
                trans = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
                                         [dmd.TransitionLayer(None, layer, Transition.TYPE_FADE, param, frame_count)])
                return (trans, True)
            else:
                return (layer, False)

    def generateLayerFromYaml(self, yaml_struct):
        """ a helper to generate Display Layers given properly formatted YAML """
        new_layer = None
        if (yaml_struct is None or (isinstance(yaml_struct, basestring) and yaml_struct == 'None')):
            return None

        try:
            if ('display' in yaml_struct):
                yaml_struct = yaml_struct['display']
                return self.generateLayerFromYaml(yaml_struct)

            elif ('Combo' in yaml_struct):
                v = yaml_struct['Combo']

                (fnt, font_style) = self.parse_font_data(v, required=False)
                msg = value_for_key(v, 'Text')
                if (msg is None):
                    self.logger.warning(
                        "Processing YAML, Combo section contains no 'Text' tag.  Consider using Animation instead.")

                new_layer = self.genMsgFrame(msg, value_for_key(v, 'Animation'), font_key=fnt, font_style=font_style)
                # Apply transforms
                #(new_layer, applied) = self.apply_transforms(new_layer, v)
                transition = value_for_key(v, 'transition', None)
                trans_length = value_for_key(v, 'trans_length', None)
                trans_param = value_for_key(v, 'trans_param', None)

                if transition is not None:
                    new_layer = dmd.TransitionLayer(None, new_layer, transitionType=transition,
                                                    transitionParameter=trans_param,
                                                    lengthInFrames=trans_length)

            elif ('Animation' in yaml_struct):
                v = yaml_struct['Animation']
                (x, y) = self.__parse_position_data(v)

                new_layer = self.game.animations[value_for_key(v, 'anim_name')]
                new_layer.reset()

                # Apply Zoom
                # if (value_for_key(v, 'zoom_layer') is not None):
                #     new_layer = self.apply_zoom(new_layer, v['zoom_layer'])

                if (value_for_key(v, 'duration') is None):  # no value found, set it so it will be later.
                    v['duration'] = new_layer.duration()

                #new_layer = self.apply_transforms(new_layer, v)
                # Apply rotation
                # if (value_for_key(v, 'rotate_layer') is not None):
                #     new_layer = self.apply_rotation(new_layer, v['rotate_layer'])
                #
                if (value_for_key(v, 'move_layer') is not None):
                    new_layer = self.apply_move(new_layer, v['move_layer'])

            elif ('sequence_layer' in yaml_struct):
                v = yaml_struct['sequence_layer']

                new_layer = dmd.ScriptlessLayer(self.game.dmd.width, self.game.dmd.height)
                repeat = value_for_key(v, 'repeat', True)

                for c in v['contents']:
                    # if not 'item' in c:
                    #     raise ValueError, "malformed YAML file; sequence must contain a list of 'item's"
                    c = c['item']
                    l = self.generateLayerFromYaml(c[0])
                    if (hasattr(l, 'duration') and callable(l.duration)):
                        def_duration = l.duration()
                    elif hasattr(l, 'duration'):
                        def_duration = new_layer.duration()
                    else:
                        def_duration = 2.0
                    d = value_for_key(c, 'duration', def_duration)
                    new_layer.append(l, d)
                # sl.set_target_position(x, y)
                new_layer.hold = not repeat

            elif ('panning_layer' in yaml_struct):
                v = yaml_struct['panning_layer']

                w = self.__parse_relative_num(v, 'width', self.game.dmd.width, None)
                h = self.__parse_relative_num(v, 'height', self.game.dmd.height, None)

                origin_x = value_for_key(v, 'origin_x', 0)
                origin_y = value_for_key(v, 'origin_y', 0)
                scroll_x = value_for_key(v, 'scroll_x', exception_on_miss=True)
                scroll_y = value_for_key(v, 'scroll_y', exception_on_miss=True)
                frames_per_movement = value_for_key(v, 'frames_per_movement', 1)
                bounce = value_for_key(v, 'bounce', False)

                c = self.generateLayerFromYaml(value_for_key(v, 'contents', exception_on_miss=True))

                new_layer = dmd.PanningLayer(width=w, height=h, frame=c, origin=(origin_x, origin_y),
                                             translate=(scroll_x, scroll_y),
                                             numFramesDrawnBetweenMovementUpdate=frames_per_movement, bounce=bounce)
                opaque = value_for_key(v, 'opaque', None)
                if opaque:
                    new_layer.opaque = opaque

            elif ('group_layer' in yaml_struct):
                v = yaml_struct['group_layer']

                (x, y) = self.__parse_position_data(v)

                w = self.__parse_relative_num(v, 'width', self.game.dmd.width, None)
                h = self.__parse_relative_num(v, 'height', self.game.dmd.height, None)

                name = value_for_key(v, 'Name', None)
                contents = value_for_key(v, 'contents', exception_on_miss=True)
                opaque = value_for_key(v, 'opaque', None)
                fill_color = value_for_key(v, 'fill_color', None)
                transition = value_for_key(v, 'transition', None)
                trans_length = value_for_key(v, 'trans_length', None)
                trans_param = value_for_key(v, 'trans_param', None)

                lyrs = []

                duration = 0
                for c in contents:
                    l = self.generateLayerFromYaml(c)
                    lyrs.append(l)
                    if (hasattr(l, 'duration') and callable(l.duration)):
                        def_duration = l.duration()
                    else:
                        def_duration = 0.0
                    d = value_for_key(c, 'duration', def_duration)
                    duration = max(d, duration)

                new_layer = dmd.GroupedLayer(w, h, lyrs, fill_color=fill_color)
                if (opaque):
                    new_layer.opaque = opaque
                new_layer.set_target_position(x, y)

                #(new_layer, applied) = self.apply_transforms(new_layer, v)

                if transition is not None:
                    new_layer = dmd.TransitionLayer(None, new_layer, transitionType=transition,
                                                    transitionParameter=trans_param,
                                                    lengthInFrames=trans_length)

            elif ('animation_layer' in yaml_struct):
                v = yaml_struct['animation_layer']

                (x, y) = self.__parse_position_data(v)

                source_layer = self.game.animations[
                    value_for_key(v, 'name', value_for_key(v, 'Name'), exception_on_miss=True)]
                source_layer.set_target_position(x, y)

                opaque = value_for_key(v, 'opaque', source_layer.opaque)
                repeat = value_for_key(v, 'repeat', source_layer.repeat)
                hold_last_frame = value_for_key(v, 'hold_last_frame', source_layer.hold)

                frame_list = value_for_key(v, 'frame_list', {})

                if (len(frame_list) == 0):
                    new_layer = source_layer
                else:
                    new_layer = AnimatedLayer(frame_time=source_layer.frame_time,
                                              frames=[source_layer.frames[idx] for idx in frame_list])

                new_layer.opaque = opaque
                new_layer.repeat = repeat
                new_layer.hold = (hold_last_frame or len(frame_list) == 1)
                new_layer.reset()

                # if (value_for_key(v, 'move_layer') is not None):
                #     new_layer = self.apply_move(new_layer, v['move_layer'])

                (new_layer, applied) = self.apply_transforms(new_layer, v, x, y)

            elif ('text_layer' in yaml_struct):
                v = yaml_struct['text_layer']

                new_layer = self.generateTextLayerFromYaml(v)
                txt = value_for_key(v, 'Text', exception_on_miss=True)

                w = self.__parse_relative_num(v, 'width', self.game.dmd.width, default=None)
                h = self.__parse_relative_num(v, 'height', self.game.dmd.height, default=None)
                x = value_for_key(v, 'x', 0)
                y = value_for_key(v, 'y', 0)

                blink_frames = value_for_key(v, 'blink_frames', None)

                new_layer.set_text(txt, blink_frames=blink_frames)

                if (w is None):
                    new_layer.width = new_layer.text_width
                if (h is None):
                    new_layer.height = new_layer.text_height

                new_layer.set_target_position(x, y)

                (new_layer, applied) = self.apply_transforms(new_layer, v)

                #(group, applied) = self.apply_transforms(dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height), v, x, y)

                # if not applied:
                #     new_layer.set_target_position(x, y)
                #     pass
                # else:
                #     new_layer = group

                # fill_color = value_for_key(v,'fill_color',(0,0,0))

            elif ('markup_layer' in yaml_struct):
                v = yaml_struct['markup_layer']

                w = self.__parse_relative_num(v, 'width', self.game.dmd.width, None)
                (bold_font, bold_style) = self.parse_font_data(value_for_key(v, 'Bold', exception_on_miss=True))
                (plain_font, plain_style) = self.parse_font_data(value_for_key(v, 'Normal', exception_on_miss=True))
                txt = value_for_key(v, "Message", exception_on_miss=True)
                if (isinstance(txt, list)):
                    txt = "\n".join(txt)

                gen = dmd.MarkupFrameGenerator(game=self.game, font_plain=plain_font, font_bold=bold_font, width=w)
                gen.set_bold_font(bold_font, interior_color=bold_style.interior_color,
                                  border_width=bold_style.line_width, border_color=bold_style.line_color)
                gen.set_plain_font(plain_font, interior_color=plain_style.interior_color,
                                   border_width=plain_style.line_width, border_color=plain_style.line_color)

                frm = gen.frame_for_markup(txt)
                new_layer = dmd.FrameLayer(frame=frm)

                #(new_layer, applied) = self.apply_transforms(new_layer, v, 0, 0)

                transition = value_for_key(v, 'transition', None)
                trans_length = value_for_key(v, 'trans_length', None)
                trans_param = value_for_key(v, 'trans_param', None)
                if transition is not None:
                    new_layer = dmd.TransitionLayer(None, new_layer, transitionType=transition,
                                                    transitionParameter=trans_param,
                                                    lengthInFrames=trans_length)

                self.prev_layer = new_layer
            elif ('move_layer' in yaml_struct):

                v = yaml_struct['move_layer']

                (fnt, font_style) = self.parse_font_data(v, required=False)
                msg = value_for_key(v, 'Text')
                if (msg is None):
                    msg = []

                start_x = value_for_key(v, 'start_x', 0)
                start_y = value_for_key(v, 'start_y', 0)
                targ_x = value_for_key(v, 'target_x', None)
                targ_y = value_for_key(v, 'target_y', None)
                frames = value_for_key(v, 'frames', 10)
                loop = value_for_key(v, 'loop', False)
                move_txt = value_for_key(v, 'move_text', True)
                move_anim = value_for_key(v, 'move_anim', False)

                anim_layer = self.genMsgFrame(msg, value_for_key(v, 'Animation'), font_key=fnt, font_style=font_style)

                if move_anim:
                    new_layer = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, [
                        dmd.moveLayer(anim_layer, start_x, start_y, targ_x, targ_y, frames, loop=loop)])
                else:
                    new_layer = anim_layer

                self.prev_layer = new_layer
            elif ('zoom_layer' in yaml_struct):

                v = yaml_struct['zoom_layer']

                (fnt, font_style) = self.parse_font_data(v, required=False)

                hold = value_for_key(v, 'hold', False)
                frames_per_zoom = value_for_key(v, 'frames_per_zoom', 1)
                scale_start = value_for_key(v, 'scale_start', 1.0)
                scale_stop = value_for_key(v, 'scale_stop', 2.0)
                total_zooms = value_for_key(v, 'total_zooms', 30)

                anim_layer = self.genMsgFrame(None, value_for_key(v, 'Animation'), font_key=fnt, font_style=font_style)
                new_layer = dmd.ZoomingLayer(anim_layer, hold, frames_per_zoom, scale_start, scale_stop, total_zooms)
            elif ('particle_layer' in yaml_struct):

                v = yaml_struct['particle_layer']

                emitters = value_for_key(v, 'emitters', None)
                if emitters is not None:
                    w = self.__parse_relative_num(v, 'width', self.game.dmd.width, None)
                    h = self.__parse_relative_num(v, 'height', self.game.dmd.height, None)

                    particle_emitters = []

                    for e in emitters:
                        x = value_for_key(e, 'x', 450)
                        y = value_for_key(e, 'y', 220)
                        max_life = value_for_key(e, 'max_life', 20)
                        max_part = value_for_key(e, 'max_particles', 200)
                        part_per_update = value_for_key(e, 'particles_per_update', 40)
                        total_creations = value_for_key(e, 'total_creations', None)
                        particle_class = value_for_key(e, 'particle_class', dmd.SnowParticle)

                        if particle_class == 'SnowParticle':
                            particle_class = dmd.SnowParticle
                        elif particle_class == 'FireParticle':
                            particle_class = dmd.FireParticle
                        elif particle_class == 'FireworkParticle':
                            particle_class = dmd.FireworkParticle

                        particle_emitters.append(dmd.ParticleEmitter(x, y, max_life,
                                                                     max_part, part_per_update, total_creations, particle_class, random_next= True))

                    new_layer = dmd.ParticleLayer(w, h, particle_emitters)

                # hold = value_for_key(v, 'hold', False)
                # frames_per_zoom = value_for_key(v, 'frames_per_zoom', 1)
                # scale_start = value_for_key(v, 'scale_start', 1.0)
                # scale_stop = value_for_key(v, 'scale_stop', 2.0)
                # total_zooms = value_for_key(v, 'total_zooms', 30)
            elif 'ScriptedText' in yaml_struct:
                v = yaml_struct['ScriptedText']

                duration = value_for_key(v, 'duration', 1.0)
                lampshow = value_for_key(v, 'lampshow')
                sound = value_for_key(v, 'sound')
                anim = value_for_key(v, 'Animation', None)
                flashing = value_for_key(v, 'flashing')

                # Trans params
                transition = value_for_key(v, 'transition', None)
                transition_out = value_for_key(v, 'transition_out', None)
                transition_param = value_for_key(v, 'trans_param', None)
                transition_out_param = value_for_key(v, 'trans_out_param', None)
                transition_length = value_for_key(v, 'trans_length', 5)
                transition_out_length = value_for_key(v, 'trans_out_length', 5)
                transition_out_duration = value_for_key(v, 'trans_out_duration', 1.0)

                (fnt, font_style) = self.parse_font_data(v, required=False)
                msg = value_for_key(v, 'TextOptions')

                if (msg is None):
                    self.logger.warning(
                        "Processing YAML, Combo section contains no 'Text' tag.  Consider using Animation instead.")

                # Create scriptless_text from lines in list
                sl = ScriptlessLayer(self.game.dmd.width, self.game.dmd.height)
                totalDuration = 0.0  # Total up the text layers created
                anim_duration = 0
                animLoaded = None

                # Prev frames to transition from
                prev_msg_frame = None

                # All Text objects in yaml Message
                for msgs in msg:
                    msgList = []
                    for line in msgs['Text']:
                        msgList.append(line)

                    #  Generate layer from the text lines, append and add duration
                    frames = self.genMsgFrame(msgList, font_style=font_style, font_key=fnt, flashing=flashing)

                    #  If all lines in text are None then create a None layer (instead of creating empty frames)
                    if len(frames.layers) > 0:

                        # The frames to show
                        tl = frames
                        # If using a transition set from prev frame to new frames
                        if transition is not None:  # Add a transition to the layer

                            tl = dmd.TransitionLayer(prev_msg_frame, tl, transitionType=transition,
                                                     transitionParameter=transition_param,
                                                     lengthInFrames=transition_length)
                        # Append to scripted layer
                        sl.append(tl, duration)

                        if transition_out is not None:
                            prev_msg_frame = dmd.TransitionLayer(tl, None,
                                                                 transitionType=transition_out,
                                                                 transitionParameter=transition_out_param,
                                                                 lengthInFrames=transition_out_length)
                            # Append transition out to scripted layer
                            sl.append(prev_msg_frame, transition_out_duration)
                    else:
                        # Add none to the script
                        sl.append(None, duration)

                    totalDuration += duration

                # add total duration and create the layer
                duration = totalDuration

                # Get the background and calculate the duration.
                if anim is not None:
                    animLoaded = self.game.animations[anim]
                    anim_duration = animLoaded.duration()

                    if anim_duration > 2.0:
                        duration = anim_duration

                # Fill up duration with None if rest of the text is none.
                if totalDuration > anim_duration:
                    duration = totalDuration
                elif totalDuration < anim_duration:
                    duration = (totalDuration - duration)
                    sl.append(None, duration)

                if animLoaded is not None:
                    new_layer = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, layers=[animLoaded, sl])
                else:
                    new_layer = dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height, layers=[sl])

                v['duration'] = duration

                # if transition is not None:
                #     lyrTmp = dmd.TransitionLayer(None, lyrTmp, transitionType=transition,
                #                                  transitionParameter=transition_param, lengthInFrames=transition_length)
            else:
                unknown_tag = None
                if (yaml_struct is not None and len(yaml_struct.keys()) > 0):
                    unknown_tag = yaml_struct.keys()[0]
                raise ValueError, "Unknown tag '%s' in yaml section.  Check spelling/caps/etc." % (unknown_tag)

        except Exception, e:
            current_tag = None
            if (yaml_struct is not None and len(yaml_struct.keys()) > 0):
                current_tag = yaml_struct.keys()[0]
            self.logger.critical(
                "YAML processing failure occured within tag '%s' of yaml section: \n'%s'" % (current_tag, yaml_struct))
            raise e

        return new_layer
