//
//  ImageLoader.m
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import "ImageLoader.h"
#import <ImageIO/ImageIO.h>

static id __instance;
static NSMutableDictionary *_connections;

@implementation ImageLoader

+ (id)sharedLoader {
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        __instance = [[[self class] alloc] init];
    });
    
    return __instance;
}

- (id)init {
    
    if ((self = [super init])) {
        
        _connections = [[NSMutableDictionary alloc] init];
        
        NSString *path = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
		path = [[path stringByAppendingPathComponent:[[NSProcessInfo processInfo] processName]] stringByAppendingPathComponent:@"ImageCache"];
		_cachePath = path;
        [[NSFileManager defaultManager] createDirectoryAtPath:_cachePath withIntermediateDirectories:YES attributes:nil error:nil];
        
    }
    return self;
    
}

- (void)imageForURL:(NSURL*)url thumb:(BOOL)thumb completion:(ImageLoaderCompletionHandler)handler {
    if (!url) return;
    
    NSString *cachePath = [NSString stringWithFormat:@"%@/%@%@", _cachePath, thumb ? @"thumb_" : @"", [url lastPathComponent]];
    
    if ([[NSFileManager defaultManager] fileExistsAtPath:cachePath]) {
        
        /*
         * Load image from disk cache
         */
        
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_LOW, 0), ^{
           
            UIImage *image = [UIImage imageWithContentsOfFile:cachePath];
            dispatch_async(dispatch_get_main_queue(), ^{
                handler(image, url);
            });
            
        });
        
    } else {
        
        /*
         * Load image from url
         */
        
        NSURLRequest *request = [[NSURLRequest alloc] initWithURL:url];
        NSURLConnection *connection = [[NSURLConnection alloc] initWithRequest:request delegate:(id<NSURLConnectionDelegate>)self];
        [connection start];
        
        NSMutableData *data = [[NSMutableData alloc] init];
        NSDictionary *connectionData = [[NSDictionary alloc] initWithObjectsAndKeys:[NSNumber numberWithBool:thumb], @"thumb", data, @"data", [handler copy], @"handler", connection, @"connection", nil];
        [_connections setObject:connectionData forKey:[url lastPathComponent]];

    }

}

- (void)imageForURL:(NSURL*)url completion:(ImageLoaderCompletionHandler)handler {
    [self imageForURL:url thumb:NO completion:handler];
}

- (void)thumbnailForURL:(NSURL*)url completion:(ImageLoaderCompletionHandler)handler {
    [self imageForURL:url thumb:YES completion:handler];
}


#pragma mark - NSURLConnectionDelegate

- (void)cancelRequestForURL:(NSURL*)url {
    
    NSString *path = [url lastPathComponent];
    
    if ([_connections objectForKey:path]) {
        NSDictionary *data = [_connections objectForKey:path];
        NSURLConnection *connection = [data objectForKey:@"connection"];
        [connection cancel];
        [_connections removeObjectForKey:path];
    }
    
}

- (void)connection:(NSURLConnection *)connection didReceiveData:(NSData *)data {
    
    NSString *path = [[[connection originalRequest] URL] lastPathComponent];
    
    if ([_connections objectForKey:path]) {
        
        NSDictionary *connection = [_connections objectForKey:path];
        NSMutableData *mutableData = [connection objectForKey:@"data"];
        [mutableData appendData:data];
        
    }
    
}

- (void)connection:(NSURLConnection *)connection didFailWithError:(NSError *)error {

    NSString *path = [[[connection originalRequest] URL] lastPathComponent];
    
    if ([_connections objectForKey:path]) {
        
        NSDictionary *connection = [_connections objectForKey:path];
        NSMutableData *data = [connection objectForKey:@"data"];
        [data appendData:data];
        
    }
    
}

- (void)connectionDidFinishLoading:(NSURLConnection *)connection {
    
    NSURL *url = [[connection originalRequest] URL];
    NSString *path = [url lastPathComponent];

    if ([_connections objectForKey:path]) {
        
        NSDictionary *connection = [_connections objectForKey:path];        
        NSMutableData *data = [connection objectForKey:@"data"];
        BOOL thumb = [[connection objectForKey:@"thumb"] boolValue];
        UIImage *image = nil;
        
        if (data && [data length] > 0) {
           
            NSString *cachePath = [NSString stringWithFormat:@"%@/%@", _cachePath, path];
            [data writeToFile:cachePath atomically:NO];
            image = [UIImage imageWithData:data];
            
            NSString *thumbPath = [NSString stringWithFormat:@"%@/%@%@", _cachePath, @"thumb_", [url lastPathComponent]];
            
            CGImageRef thumbRef = CreateThumbnailImageFromData(data, 40);
            UIImage *thumbnail = [UIImage imageWithCGImage:thumbRef];
            [UIImageJPEGRepresentation(thumbnail, 0.8) writeToFile:thumbPath atomically:NO];
            if (thumb) {
                image = thumbnail;
            }

        }
        
        ImageLoaderCompletionHandler handler = (ImageLoaderCompletionHandler)[connection objectForKey:@"handler"];

        dispatch_async(dispatch_get_main_queue(), ^{
            handler(image, url);
            [_connections removeObjectForKey:path];
        });
        
    }

}

CGImageRef CreateThumbnailImageFromData (NSData * data, int imageSize) {
    CGImageRef        myThumbnailImage = NULL;
    CGImageSourceRef  myImageSource;
    CFDictionaryRef   myOptions = NULL;
    CFStringRef       myKeys[4];
    CFTypeRef         myValues[4];
    CFNumberRef       thumbnailSize;
    
    // Create an image source from NSData; no options.
    myImageSource = CGImageSourceCreateWithData((CFDataRef)data, NULL);
    // Make sure the image source exists before continuing.
    if (myImageSource == NULL){
        fprintf(stderr, "Image source is NULL.");
        return  NULL;
    }
    
    // Package the integer as a  CFNumber object. Using CFTypes allows you
    // to more easily create the options dictionary later.
    thumbnailSize = CFNumberCreate(NULL, kCFNumberIntType, &imageSize);
    
    // Set up the thumbnail options.
    myKeys[0] = kCGImageSourceCreateThumbnailWithTransform;
    myValues[0] = (CFTypeRef)kCFBooleanTrue;
    myKeys[1] = kCGImageSourceCreateThumbnailFromImageIfAbsent;
    myValues[1] = (CFTypeRef)kCFBooleanTrue;
    myKeys[2] = kCGImageSourceThumbnailMaxPixelSize;
    myValues[2] = (CFTypeRef)thumbnailSize;
    myKeys[3] = kCGImageDestinationLossyCompressionQuality;
    myValues[3] = (CFTypeRef)[NSNumber numberWithFloat:0.8];
    
    myOptions = CFDictionaryCreate(NULL, (const void **) myKeys, (const void **) myValues, 4, &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    
    // Create the thumbnail image using the specified options.
    myThumbnailImage = CGImageSourceCreateThumbnailAtIndex(myImageSource, 0, myOptions);
    
    // Release the options dictionary and the image source
    // when you no longer need them.
    CFRelease(thumbnailSize);
    CFRelease(myOptions);
    CFRelease(myImageSource);
    
    // Make sure the thumbnail image exists before continuing.
    if (myThumbnailImage == NULL){
        fprintf(stderr, "Thumbnail image not created from image source.");
        return NULL;
    }
    
    return myThumbnailImage;
}

@end

