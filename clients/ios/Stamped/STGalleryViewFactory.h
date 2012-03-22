//
//  STGalleryViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STGallery.h"
#import "STViewDelegate.h"


@interface STGalleryViewFactory : NSObject

- (NSOperation*)createWithGallery:(id<STGallery>)gallery forBlock:(void (^)(STViewCreator))callback;

@end