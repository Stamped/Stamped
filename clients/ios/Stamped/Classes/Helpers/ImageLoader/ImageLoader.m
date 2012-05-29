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
		_cachePath = [path retain];
        [[NSFileManager defaultManager] createDirectoryAtPath:_cachePath withIntermediateDirectories:YES attributes:nil error:nil];
        
    }
    return self;
    
}

- (void)dealloc {
    [_connections release], _connections=nil;
    [_cachePath release], _cachePath=nil;
    [super dealloc];
}

- (void)imageForURL:(NSURL*)url completion:(ImageLoaderCompletionHandler)handler {
    if (!url) return;
    
    NSString *cachePath = [NSString stringWithFormat:@"%@/%@", _cachePath, [url lastPathComponent]];
    
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
        [request release];
        
        NSMutableData *data = [[NSMutableData alloc] init];
        NSDictionary *connectionData = [[NSDictionary alloc] initWithObjectsAndKeys:data, @"data", [handler copy], @"handler", connection, @"connection", nil];
        [_connections setObject:connectionData forKey:[url lastPathComponent]];
        [connection release];
        
    }

}



#pragma mark - NSURLConnectionDelegate

- (void)cancelRequestForURL:(NSURL*)url {
    
    NSString *path = [url lastPathComponent];
    
    if ([_connections objectForKey:path]) {
        NSLog(@"CANCEL");
        NSDictionary *data = [_connections objectForKey:path];
        NSURLConnection *connection = [data objectForKey:@"connection"];
        NSMutableData *mutableData = [data objectForKey:@"data"];
        [mutableData setData:nil];
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

    NSLog(@"FAILED");
    NSString *path = [[[connection originalRequest] URL] lastPathComponent];
    
    if ([_connections objectForKey:path]) {
        
        NSURL *url = [[connection originalRequest] URL];
        NSDictionary *connection = [_connections objectForKey:path];
        ImageLoaderCompletionHandler handler = (ImageLoaderCompletionHandler)[connection objectForKey:@"handler"];
        handler(nil, url);
        [_connections removeObjectForKey:path];
        
    }
    
}

- (void)connectionDidFinishLoading:(NSURLConnection *)connection {
    
    NSURL *url = [[connection originalRequest] URL];
    NSString *path = [url lastPathComponent];

    if ([_connections objectForKey:path]) {
        
        NSDictionary *connection = [_connections objectForKey:path];        
        NSMutableData *data = [connection objectForKey:@"data"];
        UIImage *image = nil;
        
        if (data!=nil && [data length] > 0) {
           
            NSString *cachePath = [NSString stringWithFormat:@"%@/%@", _cachePath, path];
            [data writeToFile:cachePath atomically:NO];
            image = [UIImage imageWithData:data];

        }
        
        ImageLoaderCompletionHandler handler = (ImageLoaderCompletionHandler)[connection objectForKey:@"handler"];

        dispatch_async(dispatch_get_main_queue(), ^{
            handler(image, url);
            [_connections removeObjectForKey:path];
        });
        
    }

}


@end

