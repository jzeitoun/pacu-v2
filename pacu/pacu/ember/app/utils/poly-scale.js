export default function polyScale(poly, spacing) {
// http://stackoverflow.com/a/11970006/796832
// Accompanying Fiddle: http://jsfiddle.net/vqKvM/35/

  var resulting_path = [];
  var N = poly.length;
  var mi, mi1, li, li1, ri, ri1, si, si1, Xi1, Yi1;

  for(var i = 0; i < N; i++) {
    mi = (poly[(i+1) % N].y - poly[i].y)/(poly[(i+1) % N].x - poly[i].x);
    mi1 = (poly[(i+2) % N].y - poly[(i+1) % N].y)/(poly[(i+2) % N].x - poly[(i+1) % N].x);
    li = Math.sqrt((poly[(i+1) % N].x - poly[i].x)*(poly[(i+1) % N].x - poly[i].x)+(poly[(i+1) % N].y - poly[i].y)*(poly[(i+1) % N].y - poly[i].y));
    li1 = Math.sqrt((poly[(i+2) % N].x - poly[(i+1) % N].x)*(poly[(i+2) % N].x - poly[(i+1) % N].x)+(poly[(i+2) % N].y - poly[(i+1) % N].y)*(poly[(i+2) % N].y - poly[(i+1) % N].y));
    ri = poly[i].x+spacing*(poly[(i+1) % N].y - poly[i].y)/li;
    ri1 = poly[(i+1) % N].x+spacing*(poly[(i+2) % N].y - poly[(i+1) % N].y)/li1;
    si = poly[i].y-spacing*(poly[(i+1) % N].x - poly[i].x)/li;
    si1 = poly[(i+1) % N].y-spacing*(poly[(i+2) % N].x - poly[(i+1) % N].x)/li1;
    Xi1 = (mi1*ri1-mi*ri+si-si1)/(mi1-mi);
    Yi1 = (mi*mi1*(ri1-ri)+mi1*si-mi*si1)/(mi1-mi);

    // Correction for vertical lines
    if(poly[(i+1) % N].x - poly[i % N].x==0) {
        Xi1 = poly[(i+1) % N].x + spacing*(poly[(i+1) % N].y - poly[i % N].y)/Math.abs(poly[(i+1) % N].y - poly[i % N].y);
        Yi1 = mi1*Xi1 - mi1*ri1 + si1;
    }

    if(poly[(i+2) % N].x - poly[(i+1) % N].x==0 ) {
        Xi1 = poly[(i+2) % N].x + spacing*(poly[(i+2) % N].y - poly[(i+1) % N].y)/Math.abs(poly[(i+2) % N].y - poly[(i+1) % N].y);
        Yi1 = mi*Xi1 - mi*ri + si;
    }

    //console.log("mi:", mi, "mi1:", mi1, "li:", li, "li1:", li1);
    //console.log("ri:", ri, "ri1:", ri1, "si:", si, "si1:", si1, "Xi1:", Xi1, "Yi1:", Yi1);

    resulting_path.push({
            x: Xi1,
            y: Yi1
        });
  }

  return resulting_path;
}

