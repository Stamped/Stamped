//
//  STGalleryViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGalleryViewFactory.h"
#import "STGalleryView.h"

@interface STGalleryOperation : NSOperation

@property (nonatomic, retain) id<STGallery> gallery;
@property (nonatomic, copy) STViewCreatorCallback callback;

@end

@implementation STGalleryOperation

@synthesize gallery = gallery_;
@synthesize callback = callback_;

- (void)dealloc {
  self.gallery = nil;
  self.callback = nil;
  [super dealloc];
}

- (void)main {
  @try {
    @autoreleasepool {
      BOOL failed = NO;
      NSMutableArray* array = [NSMutableArray array];
      if (self.gallery) {
        for (id<STGalleryItem> item in self.gallery.data) {
          @autoreleasepool {
            if ([self isCancelled]) {
              failed = YES;
              break;
            }
            NSData* data = [NSData dataWithContentsOfURL:[NSURL URLWithString:item.image]];
            UIImage* image = [UIImage imageWithData:data];
            [array addObject:image];
          }
        }
      }
      else {
        failed = YES;
      }
      if ([self isCancelled]) {
        NSLog(@"GalleryView Load Operation cancelled");
        failed = YES;
      }
      if (failed) {
        dispatch_async(dispatch_get_main_queue(), ^{
          @autoreleasepool {
            self.callback(nil);
          }
        });
      }
      else {
        dispatch_async(dispatch_get_main_queue(), ^{
          @autoreleasepool {
            if ([self isCancelled]) {
              self.callback(nil);
            }
            else {
              STViewCreator init = ^(id<STViewDelegate> delegate) {
                STGalleryView* view = [[[STGalleryView alloc] initWithGallery:self.gallery images:array andDelegate:delegate] autorelease];
                return view;
              };
              self.callback(init);
            }
          }
        });
      }
    }
  }
  @catch (NSException *exception) {
    NSLog(@"exception occurred! %@",exception);
  }
  @finally {
  }
}

@end

@implementation STGalleryViewFactory

- (NSOperation*)createWithGallery:(id<STGallery>)gallery forBlock:(void (^)(STViewCreator))callback {
  STGalleryOperation* operation = [[STGalleryOperation alloc] init];
  operation.gallery = gallery;
  operation.callback = callback;
  return [operation autorelease];
}

@end
