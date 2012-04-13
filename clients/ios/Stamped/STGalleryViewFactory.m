//
//  STGalleryViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGalleryViewFactory.h"
#import "STGalleryView.h"
#import "STViewContainer.h"

@implementation STGalleryViewFactory

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation {
  NSMutableArray* array = [NSMutableArray array];
  if ([anEntityDetail.galleries count] > 0) {
    for (id<STGallery> gallery in anEntityDetail.galleries) {
      NSMutableDictionary* dict = [NSMutableDictionary dictionary];
      for (id<STGalleryItem> item in gallery.data) {
        @autoreleasepool {
          if ([operation isCancelled]) {
            return nil;
          }
          NSData* data = [NSData dataWithContentsOfURL:[NSURL URLWithString:item.image]];
          UIImage* image = [UIImage imageWithData:data];
          [dict setObject:image forKey:item.image];
        }
      }
      [array addObject:dict];
    }
  }
  return array;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)anEntityDetail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
  STViewContainer* container = [[[STViewContainer alloc] initWithDelegate:delegate andFrame:CGRectMake(0, 0, 320, 0)] autorelease];
  NSMutableArray* array = asyncState;
  if ([anEntityDetail.galleries count] > 0) {
    for (NSInteger i = 0; i < [anEntityDetail.galleries count]; i++) {
      id<STGallery> gallery = [anEntityDetail.galleries objectAtIndex:i];
      NSDictionary* state = [array objectAtIndex:i];
      UIView* view = [[[STGalleryView alloc] initWithGallery:gallery images:state andDelegate:container] autorelease];
      [container appendChildView:view];
    }
  }
  return container;
}

@end
