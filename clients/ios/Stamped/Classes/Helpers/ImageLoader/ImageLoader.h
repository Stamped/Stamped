//
//  ImageLoader.h
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import <Foundation/Foundation.h>

typedef void(^ImageLoaderCompletionHandler)(UIImage *, NSURL *);
typedef UIImage*(^ImageLoaderStyler)(UIImage*);

@interface ImageLoader : NSObject {
    
    NSString *_cachePath;
}

+ (id)sharedLoader;

/*
 * return full size image, from cache or url
 */
- (void)imageForURL:(NSURL*)url completion:(ImageLoaderCompletionHandler)handler;

/*
 * return full size image, from cache or url, style image and cache both
 */
- (void)imageForURL:(NSURL*)url style:(ImageLoaderStyler)style styleIdentifier:(NSString*)identifier completion:(ImageLoaderCompletionHandler)handler;

/*
 * load cancelling
 */
- (void)cancelRequestForURL:(NSURL*)url;

@end
