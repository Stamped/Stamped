//
//  STGalleryViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGalleryViewFactory.h"
#import "STGalleryView.h"

@implementation STGalleryViewFactory

- (void)createWithGallery:(id<STGallery>)gallery
          andLinkDelegate:(id<STLinkDelegate>)linkDelegate
                 delegate:(id<STFactoryDelegate>)delegate
                withLabel:(id)label {
  UIView* view = [[STGalleryView alloc] initWithGallery:gallery andLinkDelegate:linkDelegate];
  [delegate didLoad:view withLabel:label];
  [view autorelease];
}

@end
