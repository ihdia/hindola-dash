window.onload = function()
{
    // var image  = document.getElementById("html5");
    // var canvas = document.createElement("canvas");
    // document.body.appendChild(canvas);

    // canvas.width  = image.width;
    // canvas.height = image.height;
    var actual_JSON = {};
    var context = 0;
    // var image1  = document.getElementById("html5");
    // console.log(image1);

    // var context = canvas.getContext("2d");
    // context.drawImage(image, 0, 0);
    loadJSON('88.json', function(response) {
  
        var actual_JSON = JSON.parse(response);
        // console.log(actual_JSON)
        var as = actual_JSON._via_img_metadata;
        var ct = 1;
        for (var key in as) {
            if (as.hasOwnProperty(key)) {
                var val = as[key];
                var filename     = val.filename;
                var image = new Image();
                // var image1  = document.getElementById("html5");
                image.src = filename;
                image.onload = function(){
                var val = as[key];
                var filename     = val.filename;
                var canvas = document.createElement("canvas");
                document.body.appendChild(canvas);
                // console.log(image);
                canvas.width  = image.width;
                canvas.height = image.height;
                context = canvas.getContext("2d");
                context.drawImage(image, 0, 0);
                var regions = val.regions;
                console.log(regions);
                context.strokeStyle = "#00008B";
                context.lineWidth = 2;
                for (var key1 in regions) {
                    if (regions.hasOwnProperty(key1)) {
                        var val = regions[key1].shape_attributes;
                        var x = val.all_points_x;
                        var y = val.all_points_y;
                        var poly = [];
                        for(var j = 0; j < x.length; j++)
                        {
                            poly.push(x[j]);
                            poly.push(y[j]);
                        }

                        context.beginPath();
                        context.moveTo(poly[0], poly[1]);
                        for( item=2 ; item < poly.length-1 ; item+=2 ){
                            context.lineTo( poly[item] , poly[item+1] );
                            
                        }
                        context.closePath();
                        context.stroke();
                    }
                    }
                }
            }
        }
    });
}; 

function loadJSON(file, callback) {   

    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', file, true); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);  
 }
