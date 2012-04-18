//
//  STAEntityDetailComponentFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAEntityDetailComponentFactory.h"
#import "Util.h"

@implementation STAEntityDetailComponentFactory

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation {
  return nil;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)anEntityDetail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
  return nil;
}

- (NSOperation*)createViewWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock {
  __block NSBlockOperation* operation = [[[NSBlockOperation alloc] init] autorelease];
  [operation addExecutionBlock:^{
    @autoreleasepool {
      @try {
        id state = [self generateAsynchronousState:anEntityDetail withOperation:operation];
        if (![operation isCancelled]) {
          dispatch_async(dispatch_get_main_queue(), ^{
            @autoreleasepool {
              STViewCreator creator = ^(id<STViewDelegate> delegate) {
                return [self generateViewOnMainLoop:anEntityDetail withState:state andDelegate:delegate];
              };
              aBlock(creator);
            }
          });
        }
      }
      @catch (NSException *exception) {
        [Util logOperationException:exception withMessage:nil];
        dispatch_async(dispatch_get_main_queue(), ^{
          @autoreleasepool {
            aBlock(nil); 
          }
        });
      }
      @finally {
      }
    }
  }];
  return operation;
}

@end
