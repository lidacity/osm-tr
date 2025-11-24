function GetClipboardText(Properties, Keys)
{
 var Result = [];
 for (const [Key, Value] of Object.entries(Properties))
  if (Keys.includes(Key))
   Result.push(`${Key}=${Value}`)
 return Result 
}


function Clipboard(Text)
{
 Text = decodeURIComponent(Text);
 Text = Text.replaceAll("\\n", "\n");
 navigator.clipboard.writeText(Text);
}


function Unpack3NF(ID, Name)
{
 return Data3NF[Name][ID]
}


function Unpack3NFsub(IDs, Name, Join)
{
 Result = new Array();
 for (Index in IDs)
 {
  ID = IDs[Index];
  Value = Data3NF[Name][ID];
  Result.push(Value);
 }
 return Result.join(Join)
}


function Popup(Feature, Layer)
{
 var Properties = Feature.properties;
 var Result = '';
 var Tag = "";
 //
 var Content = new Array();
 if (Tag = Properties['official_name'])
  Content.push(`<h3>${Tag}</h3>`);
 if (Tag = Properties['name'])
  Content.push(`<div class="popup-field"><strong>Название</strong>: ${Tag}</div>`);
 if (Tag = Properties['alt_name'])
  Content.push(`<div class="popup-field"><strong>Название</strong> (альтернативное): ${Tag}</div>`);
 if (Tag = Properties['alt_name#2'])
  Content.push(`<div class="popup-field"><strong>Название</strong> (альтернативное): ${Tag}</div>`);
 if (Tag = Properties['ref:BY:trade_register'])
  Content.push(`<div class="popup-field"><strong>Номер в реестре</strong>: <a href="?ID=${Tag}">${Tag}</a></div>`);
 if (Tag = Properties['start_date'])
  Content.push(`<div class="popup-field"><strong>Дата регистрации</strong>: ${Tag}</div>`);
 if (Tag = Properties['MTD'])
  Content.push(`<div class="popup-field"><strong>Состояние МНС</strong>: ${Tag}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Tag = Properties['addr:region'])
  Content.push(`${Tag} область`);
 if (Tag = Properties['addr:district'])
  Content.push(`${Tag} район`);
 if (Tag = Properties['addr:city'])
  Content.push(`${Tag}`);
 if (Tag = Properties['addr:street'])
  Content.push(`${Tag}`);
 if (Tag = Properties['addr:housenumber'])
  Content.push(`${Tag}`);
 if (Tag = Properties['addr:door'])
  Content.push(`${Tag}`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    <div class="popup-field"><strong>Адрес</strong>: ${Content.join(', ')}</div>
   </div>
   <hr />`
 else if (Tag = Properties['addr:full'])
  Result += `
   <div class="popup-content">
    <div class="popup-field"><strong>Адрес</strong>: ${Tag}</div>
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Tag = Properties['ref:vatin'])
  Content.push(`<div class="popup-field"><strong>УНП</strong>: <a target="_blank" href="https://etalonline.by/egr-status/${Tag}/">${Tag}</a></div>`);
 if (Tag = Properties['contact'])
  Content.push(`<div class="popup-field"><strong>Контакт</strong>: ${Tag}</div>`);
 if (Tag = Properties['type.id'])
 {
  const Text = Unpack3NF(Tag, 'type');
  Content.push(`<div class="popup-field"><strong>Тип объекта</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['format:view.id'])
 {
  const Text = Unpack3NF(Tag, 'format:view');
  Content.push(`<div class="popup-field"><strong>Вид торгового объекта</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['place:view.id'])
 {
  const Text = Unpack3NF(Tag, 'place:view');
  Content.push(`<div class="popup-field"><strong>Месторасположение</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['assortment:view.id'])
 {
  const Text = Unpack3NF(Tag, 'assortment:view');
  Content.push(`<div class="popup-field"><strong>Ассортимент</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['firm:is'])
  Content.push(`<div class="popup-field"><strong>Вид</strong>: Фирменный</div>`);
 if (Tag = Properties['amenity:type.id'])
 {
  const Text = Unpack3NF(Tag, 'amenity:type');
  Content.push(`<div class="popup-field"><strong>Тип торгового объекта</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['trade:area'])
  Content.push(`<div class="popup-field"><strong>Площадь торгового объекта</strong>: ${Tag} м²</div>`);
 if (Properties['retail:is'])
  Content.push(`<div class="popup-field"><strong>Вид торговли</strong>: Розничная</div>`);
 if (Properties['trade:is'])
  Content.push(`<div class="popup-field"><strong>Вид торговли</strong>: Оптовая</div>`);
 if (Tag = Properties['retail:place.id'])
 {
  const Text = Unpack3NF(Tag, 'retail:place');
  Content.push(`<div class="popup-field"><strong>Форма розничной торговли</strong>: ${Text}</div>`);
 }
 if (Properties['place:is'])
  Content.push(`<div class="popup-field"><strong>Оптовая торговля</strong>: Без торгового объекта</div>`);
 if (Tag = Properties['cafe:type.id'])
 {
  const Text = Unpack3NF(Tag, 'cafe:type');
  Content.push(`<div class="popup-field"><strong>Тип объекта общественного питания</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['amenity:cafe:capacity'])
  Content.push(`<div class="popup-field"><strong>Мест</strong>: ${Tag}</div>`);
 if (Tag = Properties['amenity:canteen:capacity'])
  Content.push(`<div class="popup-field"><strong>Общедоступных мест</strong>: ${Tag}</div>`);
 if (Tag = Properties['mall:specialization.id'])
 {
  const Text = Unpack3NF(Tag, 'mall:specialization');
  Content.push(`<div class="popup-field"><strong>Специализация торгового центра</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['mall:capacity'])
  Content.push(`<div class="popup-field"><strong>Торговых объектов</strong>: ${Tag}</div>`);
 if (Tag = Properties['foodcourt:capacity'])
  Content.push(`<div class="popup-field"><strong>Объектов общественного питания</strong>: ${Tag}</div>`);
 if (Tag = Properties['building:area'])
  Content.push(`<div class="popup-field"><strong>Площадь торгового центра</strong>: ${Tag} м²</div>`);
 if (Tag = Properties['marketplace:type.id'])
 {
  const Text = Unpack3NF(Tag, 'marketplace:type');
  Content.push(`<div class="popup-field"><strong>Тип рынка</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['marketplace:specialization.id'])
 {
  const Text = Unpack3NF(Tag, 'marketplace:specialization');
  Content.push(`<div class="popup-field"><strong>Специализация рынка</strong>: ${Text}</div>`);
 }
 if (Tag = Properties['marketplace:capacity'])
  Content.push(`<div class="popup-field"><strong>Торговых мест</strong>: ${Tag}</div>`);
 if (Tag = Properties['marketplace:object:capacity'])
  Content.push(`<div class="popup-field"><strong>Торговых объектов</strong>: ${Tag}</div>`);
 if (Content.length > 0)
  Result += `
   <div class="popup-content">
    ${Content.join('\n ')}
   </div>
   <hr />`;
 //
 Content = new Array();
 if (Tag = Properties['category:class.ids'])
 {
  const Title = Unpack3NFsub(Tag, 'category:class', "\n");
  const Text = Unpack3NFsub(Tag, 'category:class', "; ").substring(0, 128);
  Content.push(`<div class="popup-field" title="${Title}"><strong>Класс</strong>: <small>${Text}…</small></div>`);
 }
 if (Tag = Properties['category:group.ids'])
 {
  const Title = Unpack3NFsub(Tag, 'category:group', "\n");
  const Text = Unpack3NFsub(Tag, 'category:group', "; ").substring(0, 128);
  Content.push(`<div class="popup-field" title="${Title}"><strong>Группа</strong>: <small>${Text}…</small></div>`);
 }
 if (Tag = Properties['category:subgroup.ids'])
 {
  const Title = Unpack3NFsub(Tag, 'category:subgroup', "\n");
  const Text = Unpack3NFsub(Tag, 'category:subgroup', "; ").substring(0, 128);
  Content.push(`<div class="popup-field" title="${Title}"><strong>Подгруппа</strong>: <small>${Text}…</small></div>`);
 }
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
 var FullID = Feature.id;
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
 Address: "Дата адресов",
 Update: "Дата обновления",
};

