/* coreimage-builtins-example.m */

NSURL *url;
CIImage *source;
CIImage *result;
CIFilter *hueAdjust;

url = [NSURL fileURLWithPath:path];
source = [CIImage imageWithContentsOfURL:url];

hueAdjust = [CIFilter filterWithName:@"CIHueAdjust"];
[hueAdjust setValue:source forKey:@"inputImage"];
[hueAdjust setValue:[NSNumber numberWithFloat:2.094] 
           forKey:@"inputAngle"];

result = [hueAdjust valueForKey:@"outputImage"]; 
