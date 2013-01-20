from collections import Counter
import copy
from . import HairballPlugin, PluginView, PluginWrapper


class BlockTypesView(PluginView):
    def view(self, data):
        blocks = ""
        for block, count in data['types']:
            blocks += "{1:{2}} {0}".format(str(count), block, 30) + '<br />'
        return '<p>{0}</p>'.format(blocks)


class BlockTypes(HairballPlugin):
    """Block Types

    Produces a count of each type of block contained in a scratch file.
    """
    @PluginWrapper(html=BlockTypesView)
    def analyze(self, scratch):
        blocks = Counter()
        scripts = scratch.stage.scripts[:]
        [scripts.extend(x.scripts) for x in scratch.stage.sprites]
        for script in scripts:
            for name, level, block in self.iter_blocks(script.blocks):
                blocks.update({name: 1})
        return self.view_data(types=blocks.most_common())


class BlockTotals(HairballPlugin):
    """Block Totals

    Produces a count of each type of block contained in all the scratch files.
    """
    def __init__(self):
        super(BlockTotals, self).__init__()
        self.blocks = Counter()

    def finalize(self):
        for name, count in sorted(self.blocks.items(), key=lambda x: x[1]):
            print('{0:3} {1}'.format(count, name))
        print('{0:3} total'.format(sum(self.blocks.values())))

    def analyze(self, scratch):
        scripts = scratch.stage.scripts[:]
        [scripts.extend(x.scripts) for x in scratch.stage.sprites]
        for script in scripts:
            for name, level, block in self.iter_blocks(script.blocks):
                self.blocks.update({name: 1})
        return self.view_data(types=self.blocks)


class DeadCodeView(PluginView):
    def view(self, data):
        dead = ""
        (variable_event, deadcode) = data['deadcode']
        if len(deadcode) == 0:
            dead = '<p>No Dead Code</p>'
        else:
            if variable_event:
                dead = '<p>Warning: Contains variable-event broadcasts</p>'
            for sprite in deadcode.keys():
                if len(deadcode[sprite]) != 0:
                    dead += self.to_scratch_blocks(
                        sprite, deadcode[sprite])
        return dead


class DeadCode(HairballPlugin):
    """Dead Code

    Shows all of the dead code for each sprite in a scratch file.
    """
    def __init__(self):
        super(DeadCode, self).__init__()
        self.dead = {}

    def finalize(self):
        file = open('deadcode.txt', 'w')
        file.write("activity, pair, variable_event, sprites with dead code\n")
        for ((group, project), (variable_event, sprite_dict)) in\
                self.blocks.items():
            file.write('\n')
            file.write(project)
            file.write(', ')
            file.write(group)
            file.write(', ')
            file.write(variable_event)
            for key in sprite_dict.keys():
                file.write(', ')
                file.write(key)

    @PluginWrapper(html=DeadCodeView)
    def analyze(self, scratch):
        sprites = {}
        scripts = scratch.stage.scripts[:]
        [scripts.extend(x.scripts) for x in scratch.stage.sprites]
        for script in scripts:
            if script.morph.name not in sprites.keys():
                sprites[script.morph.name] = []
            if not script.reachable:
                sprites[script.morph.name].append(script)
        variable_event = True in self.get_broadcast_events(scripts)
        if hasattr(scratch, 'group') and hasattr(scratch, 'project'):
            self.dead[(scratch.group, scratch.project)] = (
                variable_event, copy.deepcopy(sprites))
        return self.view_data(deadcode=(variable_event, sprites))


class ScriptImagesView(PluginView):
    def view(self, data):
        script_images = ""
        for sprite in data['scripts'].keys():
            script_images += self.to_scratch_blocks(
                sprite, data["scripts"][sprite])
        return script_images


class ScriptImages(HairballPlugin):
    """The Script Images

    Shows all of the scripts for each sprite in a scratch file.
    """
    @PluginWrapper(html=ScriptImagesView)
    def __init__(self):
        super(ScriptImages, self).__init__()
        self.script_images = {}

    def finalize(self):
        file = open('scriptimages.html', 'w')
        for sprite in self.script_images.keys():
            file.write(
                self.to_scratch_blocks(sprite, self.script_images[sprite]))

    def analyze(self, scratch):
        for sprite in scratch.stage.sprites:
            self.script_images[sprite.name] = []
            for script in sprite.scripts:
                self.script_images[sprite.name].append(script)
        self.script_images["stage"] = []
        for script in scratch.stage.scripts:
            self.script_images["stage"].append(script)
        return self.view_data(scripts=self.script_images)
