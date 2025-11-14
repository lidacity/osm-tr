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


function Popup(Feature, Layer)
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
 if (Properties['ref:BY:trade_register'])
  Content.push(`<div class="popup-field"><strong>Номер в реестре</strong>: <a href="?ID=${Properties['ref:BY:trade_register']}">${Properties['ref:BY:trade_register']}</a></div>`);
 if (Properties['start_date'])
  Content.push(`<div class="popup-field"><strong>Дата регистрации</strong>: ${Properties['start_date']}</div>`);
 if (Properties['MTD'])
  Content.push(`<div class="popup-field"><strong>Состояние МНС</strong>: ${Properties['MTD']}</div>`);
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
 if (Properties['ref:vatin'])
  Content.push(`<div class="popup-field"><strong>УНП</strong>: <a target="_blank" href="https://etalonline.by/egr-status/${Properties['ref:vatin']}/">${Properties['ref:vatin']}</a></div>`);
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
 if (Properties['category:class.ids'])
  Content.push(`<div class="popup-field"><strong>Класс</strong>: ${Unpack3NFsub(Properties, 'category:class')}</div>`);
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
 var FullID = Properties['ID'];
 if (FullID)
 {
  var ShortType = Array.from(FullID)[0];
  var ID = FullID.substring(1);
  var Type = '';
  if (ShortType == 'n')
   Type = 'node';
  if (ShortType == 'w')
   Type = 'way';
  Content.push(`<a target="_blank" href="https://openstreetmap.org/${Type}/${ID}">osm</a>`);
  Content.push(`<a target="_josm" href="http://localhost:8111/load_object?objects=${FullID}&relation_members=true&referrers=true" onclick='return LoadObject("${FullID}");'>josm</a>`);
  Content.push(`<a target="_id" href="https://www.openstreetmap.org/edit?${ShortType}=${ID}#map=19/${Lat}/${Lon}");'>iD</a>`);
  Content.push(`<a target="_blank" href="https://pewu.github.io/osm-history/#/${Type}/${ID}">history</a>`);
  Content.push(`<a target="_blank" href="https://mapillary.com/app/?lat=${Lat}&lng=${Lon}&z=18">Mapillary</a>`);
 }
 else if (["orange", "red"].includes(Properties['status']))
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


var DateLegend =
{
 Trade: "Дата торгового реестра",
 Geofabrik: "Дата geofabrik", //
 MTD: "Дата МНС", 
 Nominatim: "Дата nominatim", //
 Address: "Дата адресов",
 Update: "Дата обновления",
};

