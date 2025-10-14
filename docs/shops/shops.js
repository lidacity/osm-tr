const LayerMain = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap contributors'});
const LayerGray = new L.TileLayer.Grayscale('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap contributors'});
//const LayerHot = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {attribution: '© OpenStreetMap contributors'});
//const LayerMapbox = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {attribution: 'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>', id: 'TR', accessToken: 'pk.eyJ1IjoibGlkYWNpdHkiLCJhIjoiY21ma3Yzc2czMDB5MTJsc2Jnajg2aG9taCJ9.F7iCB_GkZFAa-MHxF4H27w'});

var BaseMaps = {
 "OpenStreetMap": LayerMain,
 "OpenStreetMap.Gray": LayerGray,
// "OpenStreetMap.HOT": LayerHot,
// "Mapbox": LayerMapbox,
};

var MapOption =
{
 center: new L.LatLng(53.90, 27.56),
 zoom: 7,
 layers: [LayerGray],
 fadeAnimation: false,
}

var OptionIcon =
{
 iconSize: [25, 41],
 iconAnchor: [12, 41],
 popupAnchor: [1, -34],
}

var LeafIcon = L.Icon.extend({options: OptionIcon});

var Group =
{
 green: L.layerGroup([], {title: 'Всё в порядке', short: 'Ok', icon: new LeafIcon({iconUrl: './img/marker-icon-green.png'}), }),
 blue: L.layerGroup([], {title: 'Совпадение имени', short: 'Имя', icon: new LeafIcon({iconUrl: './img/marker-icon-blue.png'}), }),
 orange: L.layerGroup([], {title: 'Совпадение места', short: 'Место', icon: new LeafIcon({iconUrl: './img/marker-icon-orange.png'}), }),
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
}


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
 var Icon = Group[Feature.properties.status].options.icon;
 var Marker = L.marker(LatLng, {icon: Icon, title: Feature.properties.status});
 Marker.addTo(Group[Feature.properties.status]);
 Storage.set(Feature.properties['ref:BY:trade_register'], Marker);
 return Marker;
}


function Unpack3NF(Properties, Name)
{
 var ID = Properties[`${Name}.id`];
 return Data3NF[Name][ID];
}


function Unpack3NFsub(Properties, Name)
{
 Result = new Array();
 var IDs = Properties[`${Name}.ids`];
 for (Index in IDs)
 {
  ID = IDs[Index];
  Value = Data3NF[Name][ID];
  Result.push(Value);
 }
 return Result.join('\n');
}


function JsonEachFeature(Feature, Layer)
{
 var Properties = Feature['properties'];
 var Result = '';
 //
 var Content = new Array();
 if (Properties['official_name'])
  Content.push(`<h3>${Properties['official_name']}</h3>`);
 if (Properties['name'])
  Content.push(`<div class="popup-field"><strong>Название</strong>: ${Properties['name']}</div>`);
 if (Properties['alt_name'])
  Content.push(`<div class="popup-field"><strong>Название</strong> (альтернативное): ${Properties['alt_name']}</div>`);
 if (Properties['alt_name#2'])
  Content.push(`<div class="popup-field"><strong>Название</strong> (альтернативное): ${Properties['alt_name#2']}</div>`);
 Content.push(`<div class="popup-field"><strong>Номер в реестре</strong>: <a href="?ID=${Properties['ref:BY:trade_register']}">${Properties['ref:BY:trade_register']}</a></div>`);
 Content.push(`<div class="popup-field"><strong>Дата регистрации</strong>: ${Properties['start_date']}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Properties['addr:region'])
  Content.push(`${Properties['addr:region']} область`);
 if (Properties['addr:district'])
  Content.push(`${Properties['addr:district']} район`);
 if (Properties['addr:city'])
  Content.push(`населенный пункт ${Properties['addr:city']}`);
 if (Properties['addr:street'])
  Content.push(`улица ${Properties['addr:street']}`);
 if (Properties['addr:housenumber'])
  Content.push(`${Properties['addr:housenumber']}`);
 if (Properties['addr:door'])
  Content.push(`${Properties['addr:door']}`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    <div class="popup-field"><strong>Адрес</strong>: ${Content.join(', ')}</div>
   </div>
   <hr />`
 else if (Properties['addr:full'])
  Result += `
   <div class="popup-content">
    <div class="popup-field"><strong>Адрес</strong>: ${Properties['addr:full']}</div>
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Properties['operator:ref:BY:PAN'])
  Content.push(`<div class="popup-field"><strong>УНП</strong>: <a target="_blank" href="https://etalonline.by/egr-status/${Properties['operator:ref:BY:PAN']}/">${Properties['operator:ref:BY:PAN']}</a></div>`);
 if (Properties['contact'])
  Content.push(`<div class="popup-field"><strong>Контакт</strong>: ${Properties['contact']}</div>`);
 if (Properties['type.id'])
  Content.push(`<div class="popup-field"><strong>Тип объекта</strong>: ${Unpack3NF(Properties, 'type')}</div>`);
 if (Properties['format:view.id'])
  Content.push(`<div class="popup-field"><strong>Вид торгового объекта</strong>: ${Unpack3NF(Properties, 'format:view')}</div>`);
 if (Properties['place:view.id'])
  Content.push(`<div class="popup-field"><strong>Месторасположение</strong>: ${Unpack3NF(Properties, 'place:view')}</div>`);
 if (Properties['assortment:view.id'])
  Content.push(`<div class="popup-field"><strong>Ассортимент</strong>: ${Unpack3NF(Properties, 'assortment:view')}</div>`);
 if (Properties['firm:is'])
  Content.push(`<div class="popup-field"><strong>Вид</strong>: Фирменный</div>`);
 if (Properties['amenity:type.id'])
  Content.push(`<div class="popup-field"><strong>Тип торгового объекта</strong>: ${Unpack3NF(Properties, 'amenity:type')}</div>`);
 if (Properties['trade:area'])
  Content.push(`<div class="popup-field"><strong>Площадь торгового объекта</strong>: ${Properties['trade:area']} м²</div>`);
 if (Properties['retail:is'])
  Content.push(`<div class="popup-field"><strong>Вид торговли</strong>: Розничная</div>`);
 if (Properties['trade:is'])
  Content.push(`<div class="popup-field"><strong>Вид торговли</strong>: Оптовая</div>`);
 if (Properties['retail:place.id'])
  Content.push(`<div class="popup-field"><strong>Форма розничной торговли</strong>: ${Unpack3NF(Properties, 'retail:place')}</div>`);
 if (Properties['place:is'])
  Content.push(`<div class="popup-field"><strong>Оптовая торговля</strong>: Без торгового объекта</div>`);
 if (Properties['cafe:type.id'])
  Content.push(`<div class="popup-field"><strong>Тип объекта общественного питания</strong>: ${Unpack3NF(Properties, 'cafe:type')}</div>`);
 if (Properties['amenity:cafe:capacity'])
  Content.push(`<div class="popup-field"><strong>Мест</strong>: ${Properties['amenity:cafe:capacity']}</div>`);
 if (Properties['amenity:canteen:capacity'])
  Content.push(`<div class="popup-field"><strong>Общедоступных мест</strong>: ${Properties['amenity:canteen:capacity']}</div>`);
 if (Properties['mall:specialization.id'])
  Content.push(`<div class="popup-field"><strong>Специализация торгового центра</strong>: ${Unpack3NF(Properties, 'mall:specialization')}</div>`);
 if (Properties['mall:capacity'])
  Content.push(`<div class="popup-field"><strong>Торговых объектов</strong>: ${Properties['mall:capacity']}</div>`);
 if (Properties['foodcourt:capacity'])
  Content.push(`<div class="popup-field"><strong>Объектов общественного питания</strong>: ${Properties['foodcourt:capacity']}</div>`);
 if (Properties['building:area'])
  Content.push(`<div class="popup-field"><strong>Площадь торгового центра</strong>: ${Properties['building:area']} м²</div>`);
 if (Properties['marketplace:type.id'])
  Content.push(`<div class="popup-field"><strong>Тип рынка</strong>: ${Unpack3NF(Properties, 'marketplace:type')}</div>`);
 if (Properties['marketplace:specialization.id'])
  Content.push(`<div class="popup-field"><strong>Специализация рынка</strong>: ${Unpack3NF(Properties, 'marketplace:specialization')}</div>`);
 if (Properties['marketplace:capacity'])
  Content.push(`<div class="popup-field"><strong>Торговых мест</strong>: ${Properties['marketplace:capacity']}</div>`);
 if (Properties['marketplace:object:capacity'])
  Content.push(`<div class="popup-field"><strong>Торговых объектов</strong>: ${Properties['marketplace:object:capacity']}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Properties['category:class.id'])
  Content.push(`<div class="popup-field"><strong>Класс</strong>: ${Unpack3NF(Properties, 'category:class')}</div>`);
 if (Properties['category:group.ids'])
  Content.push(`<div class="popup-field" title="${Unpack3NFsub(Properties, 'category:group')}"><strong>Группа</strong>: {скрыто}</div>`);
 if (Properties['category:subgroup.ids'])
  Content.push(`<div class="popup-field" title="${Unpack3NFsub(Properties, 'category:subgroup')}"><strong>Подгруппа</strong>: {скрыто}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 if (Properties['status'] != "green")
 {
  Result += `
   <div class="popup-content">
    <div class="popup-field">ref:BY:trade_register=${Properties['ref:BY:trade_register']} &nbsp; <button id="clipboard" onclick="Clipboard('ref:BY:trade_register=${Properties['ref:BY:trade_register']}');">копировать</button></div>
   </div>
   <hr />`;
 }
 //
 Content = new Array();
 var Lat = Feature.geometry.coordinates[1];
 var Lon = Feature.geometry.coordinates[0];
 if (Properties['ID'])
 {
  ShortType = Array.from(Properties['ID'])[0];
  ID = Properties['ID'].substring(1);
  Type = '';
  if (ShortType == 'n')
   Type = 'node';
  if (ShortType == 'w')
   Type = 'way';
  Content.push(`<a target="_blank" href="https://openstreetmap.org/${Type}/${ID}">osm</a>`);
  Content.push(`<a target="_josm" href="http://localhost:8111/load_object?objects=${Properties['ID']}&relation_members=true&referrers=true" onclick='return LoadObject("${Properties['ID']}");'>josm</a>`);
  Content.push(`<a target="_blank" href="https://pewu.github.io/osm-history/#/${Type}/${ID}">history</a>`);
  Content.push(`<a target="_blank" href="https://mapillary.com/app/?lat=${Lat}&lng=${Lon}&z=18">Mapillary</a>`);
 }
 else if (Properties['status'] == "red")
 {
  Content.push(`<a target="_blank" href="https://openstreetmap.org/#map=17/${Lat}/${Lon}" target="_blank">osm</a>`);
  Content.push(`<a target="_josm" href="http://localhost:8111/load_and_zoom?left=${Lon}&top=${Lat}&right=${Lon}&bottom=${Lat}" onclick='return LoadAndZoom(${Lat}, ${Lon});'>josm</a>`);
  Content.push(`<a target="_blank" href="https://mapillary.com/app/?lat=${Lat}&lng=${Lon}&z=18">Mapillary</a>`);
 }
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    <div class="popup-field">${Content.join('&nbsp;&nbsp;')}</div>
   </div>`;
 //
 Layer.bindPopup(Result);
}


function Clipboard(Text)
{
 navigator.clipboard.writeText(Text);
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
 content: `Дата торгового реестра: ${ModifyDate['Trade']}\nДата nominatim: ${ModifyDate['Nominatim']}\nДата geofabrik: ${ModifyDate['Geofabrik']}\nДата обновления: ${ModifyDate['Update']}\nВсего: ${Total}`,
 opacity: 0.5,
 legends: Legends,
 collapsed: true,
}).addTo(Map);


const UrlParams = new URLSearchParams(window.location.search);
const MarkerId = UrlParams.get('ID');
if (MarkerId && Storage.has(MarkerId))
{
 const Marker = Storage.get(MarkerId);
 if (Marker)
  Markers.zoomToShowLayer(Marker, () => { Marker.openPopup(); });
}


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
