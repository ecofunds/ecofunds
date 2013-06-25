from gmapi.maps import MapConstantClass, MapClass, Args

SymbolPath = MapConstantClass('SymbolPath',
                             ('CIRCLE',))

class Circle(MapClass):

    _getopts = {

    }
    _setopts = {
        'setMap': 'map',
    }

    def __init__(self, opts=None):
        super(Circle, self).__init__(cls='Circle')
        self._map = None
        self['arg'] = Args(['opts'])
        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        if 'strokeColor' in opts:
            color = 'color:0x%s' % opts['strokeColor'].lstrip('#').lower()
            if 'strokeOpacity' in opts:
                color += '%02x' % min(max(opts['strokeOpacity'] * 255, 0), 255)
            params.append(color)
        if 'strokeWeight' in opts:
            params.append('weight:%d' % opts['strokeWeight'])
        return '|'.join(params)

    def getMap(self):
        return self._map

    def setOptions(self, options):
        if options and 'map' in options:
            if self._map:
                # Remove this polyline from the map.
                self._map['crl'].remove(self)
            # Save new map reference.
            self._map = options.pop('map')
            if self._map:
                self._map.setdefault('crl', []).append(self)

        super(Circle, self).setOptions(options)


class Label(MapClass):

    def __init__(self, opts=None):
        super(Label, self).__init__(cls='Label', context='')
        self._map = None
        self['arg'] = Args(['opts'])

        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        return '|'.join(params)

    def getMap(self):
        return self._map

    def setOptions(self, options):
        if options and 'map' in options:
            self._map = options.pop('map')
        if self._map:
            self._map.setdefault('lbl', []).append(self)

        super(Label, self).setOptions(options)

class MarkerClusterer(MapClass):
    _getopts = {
        'getMarkers': 'markers',
    }
    _setopts = {
        'setMarkers': 'markers',
    }

    def __init__(self, map, markers, opts=None):
        super(MarkerClusterer, self).__init__(cls='MarkerClusterer', context='', mapIntoConstructor=True)
        self._map = map
        self['arg'] = Args(['map', 'markers', 'opts'])

        if map:
            self['arg'].setdefault('map', {})
        if markers:
            self['arg'].setdefault('markers', [])

        self.setOptions(opts)

    def __unicode__(self):
        opts = self['arg'].get('opts', {})
        params = []
        return '|'.join(params)

    def getMap(self):
        return self._map

    def setOptions(self, options):
        if options and 'map' in options:
            self._map = options.pop('map')
        if self._map:
            self._map.setdefault('mkc', []).append(self)

        super(MarkerClusterer, self).setOptions(options)

class InfoBubble(MapClass):
    _getopts = {
        'getContent': 'content',
        'getPosition': 'position',
        'getShadowStyle': 'shadowStyle',
        'getPadding': 'padding',
        'getBackgroundColor': 'backgroundColor',
        'getBorderRadius': 'borderRadius',
        'getArrowSize': 'arrowSize',
        'getBorderWidth': 'borderWidth',
        'getBorderColor': 'borderColor',
        'getDisableAutoPan': 'disableAutoPan',
        'getHideCloseButton': 'hideCloseButton',
        'getArrowPosition': 'arrowPosition',
        'getArrowDirection': 'arrowDirection',
        'getBackgroundClassName': 'backgroundClassName',
        'getArrowStyle': 'arrowStyle'
    }
    _setopts = {
        'setContent': 'content',
        'setPosition': 'position',
        'setShadowStyle': 'shadowStyle',
        'setPadding': 'padding',
        'setBackgroundColor': 'backgroundColor',
        'setBorderRadius': 'borderRadius',
        'setArrowSize': 'arrowSize',
        'setBorderWidth': 'borderWidth',
        'setBorderColor': 'borderColor',
        'setDisableAutoPan': 'disableAutoPan',
        'setHideCloseButton': 'hideCloseButton',
        'setArrowPosition': 'arrowPosition',
        'setArrowDirection': 'arrowDirection',
        'setBackgroundClassName': 'backgroundClassName',
        'setArrowStyle': 'arrowStyle'
    }

    def __init__(self, opts=None):
        super(InfoBubble, self).__init__(cls='InfoBubble', context='')
        self._map = None
        self['arg'] = Args(['opts'])
        self.setOptions(opts)

    def open(self, map, anchor=None):
        if anchor:
            anchor.setMap(map)
            anchor['nfo'] = self
        else:
            map['nfo'] = self