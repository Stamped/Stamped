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
                 delegate:(id<STViewDelegate>)delegate
                withLabel:(id)label {
  UIView* view = nil;
  if (gallery) {
    view = [[STGalleryView alloc] initWithGallery:gallery andDelegate:delegate];
    [view autorelease];
  }
  [delegate didLoad:view withLabel:label];
}

@end
