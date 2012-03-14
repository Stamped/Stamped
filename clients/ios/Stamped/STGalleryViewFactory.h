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

- (void)createWithGallery:(id<STGallery>)gallery
                 delegate:(id<STViewDelegate>)delegate
                withLabel:(id)label;

@end
