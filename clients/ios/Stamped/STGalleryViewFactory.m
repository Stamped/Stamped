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

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation {
  NSMutableDictionary* dict = [NSMutableDictionary dictionary];
  if (anEntityDetail.gallery) {
    for (id<STGalleryItem> item in anEntityDetail.gallery.data) {
      @autoreleasepool {
        if ([operation isCancelled]) {
          return nil;
        }
        NSData* data = [NSData dataWithContentsOfURL:[NSURL URLWithString:item.image]];
        UIImage* image = [UIImage imageWithData:data];
        [dict setObject:image forKey:item.image];
      }
    }
  }
  return dict;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)anEntityDetail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
  return [[[STGalleryView alloc] initWithGallery:anEntityDetail.gallery images:asyncState andDelegate:delegate] autorelease];
}

@end
