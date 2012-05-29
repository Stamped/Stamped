//
//  ImageLoader.h
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import <Foundation/Foundation.h>

typedef  void(^ImageLoaderCompletionHandler)(UIImage *, NSURL *);

@interface ImageLoader : NSObject {
    
    NSString *_cachePath;
}

+ (id)sharedLoader;

/*
 * return full size image, from cache or url
 */
- (void)imageForURL:(NSURL*)url completion:(ImageLoaderCompletionHandler)handler;

/*
 * return thumbnail sized image, from cache or url
 */
- (void)thumbnailForURL:(NSURL*)url completion:(ImageLoaderCompletionHandler)handler;

@end
