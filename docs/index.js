const LayerMain = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap contributors'});
const LayerGray = new L.TileLayer.Grayscale('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap contributors'});

var BaseMaps = {
 "OpenStreetMap": LayerMain,
 "OpenStreetMap.Gray": LayerGray,
};

var MapOption =
{
 center: new L.LatLng(53.90, 27.56),
 zoom: 7,
 layers: [LayerGray],
 fadeAnimation: false,
};

var OptionIcon =
{
 iconSize: [25, 41],
 iconAnchor: [12, 41],
 popupAnchor: [1, -34],
};

var LeafIcon = L.Icon.extend({options: OptionIcon});

var Group =
{
 green: L.layerGroup([], {title: 'Всё в порядке', short: 'Ok', icon: new LeafIcon({iconUrl: './img/marker-icon-green.png'}), }),
 blue: L.layerGroup([], {title: 'Совпадение имени', short: 'Имя', icon: new LeafIcon({iconUrl: './img/marker-icon-blue.png'}), }),
 violet: L.layerGroup([], {title: 'Совпадение места', short: 'Место', icon: new LeafIcon({iconUrl: './img/marker-icon-violet.png'}), }),
 orange: L.layerGroup([], {title: 'Совпадение адреса', short: 'Адрес', icon: new LeafIcon({iconUrl: './img/marker-icon-orange.png'}), }),
 gold: L.layerGroup([], {title: 'Повторы', short: 'Дубли', icon: new LeafIcon({iconUrl: './img/marker-icon-gold.png'}), }),
 grey: L.layerGroup([], {title: 'В процессе ликвидации', short: 'Ликвидация', icon: new LeafIcon({iconUrl: './img/marker-icon-grey.png'}), }),
 black: L.layerGroup([], {title: 'Нет в реестре, но есть на карте', short: 'Ошибка', icon: new LeafIcon({iconUrl: './img/marker-icon-black.png'}), }),
 red: L.layerGroup([], {title: 'Не найден', short: 'Отсутстует', icon: new LeafIcon({iconUrl: './img/marker-icon-red.png'}), }),
};


var Orders = new Array();
var Titles = {};
var ColorDicts = {};
for (const [Color, Layer] of Object.entries(Group))
{
 Orders.push(Color);
 Titles[Color] = Layer.options.short;
 ColorDicts[Color] = Color;
};

var MarkerOption =
{
 key: 'title',
 order: Orders,
 title: Titles,
 arcColorDict: ColorDicts,
 style: {size: 40, fill: '#ddd', opacity: 0.7, weight: 7}, //'donut-style',
 textClassName: 'donut-text',
 legendClassName: 'donut-legend',
};

var Markers = L.DonutCluster({chunkedLoading: true}, MarkerOption);

const Storage = new Map();

var DataOption =
{
 style: GetStyle,
 filter: GetFilter,
 pointToLayer: PointToLayer,
 onEachFeature: JsonEachFeature,
};


// -=-=-=-=-=-


function GetStyle(Feature)
{
  return { "color": Feature.properties.status, "weight": 5, "opacity": 0.65, };
}


function GetFilter(Feature, Layer)
{
 return true;
}


function PointToLayer(Feature, LatLng)
{
 if ('status' in Feature.properties)
 {
  var Icon = Group[Feature.properties.status].options.icon;
  var Marker = L.marker(LatLng, {icon: Icon, title: Feature.properties.status});
  Marker.addTo(Group[Feature.properties.status]);
  Storage.set(Feature.properties['ref:BY:trade_register'], Marker);
  return Marker;
 }
}


function JsonEachFeature(Feature, Layer)
{
 Popup(Feature, Layer)
}


function Clipboard(Text)
{
 navigator.clipboard.writeText(Text);
}


function GetUrlParams(Param, Default)
{
 const UrlParams = new URLSearchParams(window.location.search);
 const Result = UrlParams.get(Param);
 if (Result)
  return Result
 else
  return Default
}


function GetDates()
{
 var Result = [];
 for (const [Key, Value] of Object.entries(DateLegend))
  Result.push(`${Value}: ${ModifyDate[Key]}`);
 return Result.join('\n');
}


// -=-=-=-=-=-


var Map = L.map('map', MapOption);
var Control = L.control.layers(BaseMaps, null).addTo(Map);

Markers.addTo(Map);
var GeoJsonLayer = L.geoJSON(Data, DataOption);
Map.fitBounds(GeoJsonLayer.getBounds().pad(0.1));

for (const [Color, Layer] of Object.entries(Group))
{
 Markers.checkIn(Layer);
 Control.addOverlay(Layer, Layer.options.title);
 Layer.addTo(Map);
};
Control.addTo(Map);


// -=-=-=-=-=-


var ContextMenu = L.popup();

Map.on('contextmenu', function(e) {
 var Lat = e.latlng.lat.toFixed(7);
 var Lon = e.latlng.lng.toFixed(7);
 //var Zoom = Map.getZoom();
 ContextMenu
  .setLatLng(e.latlng)
  .setContent(`
   <div class="context-menu">
    Открыть в:<br />
    &nbsp;- <a target="_blank" href="https://openstreetmap.org/#map=17/${Lat}/${Lon}">osm</a><br/>
    &nbsp;- <a target="_josm" href="http://localhost:8111/load_and_zoom?left=${Lon}&top=${Lat}&right=${Lon}&bottom=${Lat}" onclick='return LoadAndZoom(${Lat}, ${Lon});'>josm</a><br/>
    &nbsp;- <a target="_blank" href="https://mapillary.com/app/?lat=${Lat}&lng=${Lon}&z=18">Mapillary</a>
   </div>
  `).openOn(Map);
  });

Map.on('click', function(e) {
 console.log('[' + e.latlng.lat + ', ' + e.latlng.lng + ']');
});

var Legends = new Array();
var Total = 0;
for (const [Color, Layer] of Object.entries(Group))
{
 var Count = Layer.getLayers().length;
 Total += Count;
 var Legend =
 {
  label: Layer.options.title + ' (' + Count + ')',
  type: "image",
  url: Layer.options.icon.options.iconUrl,
 }
 Legends.push(Legend);
};


L.control.Legend({
 position: "bottomright",
 title: "Статистика",
 content: GetDates() + `\nВсего: ${Total}`,
 opacity: 0.5,
 legends: Legends,
 collapsed: true,
}).addTo(Map);


const MarkerId = GetUrlParams('ID', null);
if (MarkerId && Storage.has(MarkerId))
{
 const Marker = Storage.get(MarkerId);
 if (Marker)
  Markers.zoomToShowLayer(Marker, () => { Marker.openPopup(); });
}


// -=-=-=-=-=-


function LoadAndZoom(Lat, Lon)
{
 document.getElementById('JOSM').src = `http://localhost:8111/load_and_zoom?left=${Lon-0.01}&top=${Lat+0.005}&right=${Lon+0.01}&bottom=${Lat-0.005}`;
 return false;
}


function LoadObject(ID)
{
 document.getElementById('JOSM').src = `http://localhost:8111/load_object?objects=${ID}&relation_members=true&referrers=true`;
 return false;
}
