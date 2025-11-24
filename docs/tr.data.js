function СoncatGeoJSON(g1, g2, g3, g4, g5, g6, g7, g8)
{
 return { 
  "type" : "FeatureCollection",
  "features": g1.features.concat(g2.features.concat(g3.features.concat(g4.features.concat(g5.features.concat(g6.features.concat(g7.features.concat(g8.features))))))),
 }
}

var Data = СoncatGeoJSON(Data1, Data2, Data3, Data4, Data5, Data6, Data7, Data8);
