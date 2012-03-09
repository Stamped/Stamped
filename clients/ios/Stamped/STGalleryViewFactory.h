//
//  STGalleryViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STGallery.h"
#import "STLinkDelegate.h"
#import "STFactoryDelegate.h"

@interface STGalleryViewFactory : NSObject

- (void)createWithGallery:(id<STGallery>)gallery
          andLinkDelegate:(id<STLinkDelegate>)linkDelegate
                 delegate:(id<STFactoryDelegate>)delegate
                withLabel:(id)label;

@end
