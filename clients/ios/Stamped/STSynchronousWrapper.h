//
//  STSynchronousWrapper.h
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STEntityDetailComponentFactory.h"

typedef void (^STSynchronousWrapperCallback)();

@interface STSynchronousWrapper : STViewContainer

- (id)initWithDelegate:(id<STViewDelegate>)delegate
      componentFactory:(id<STEntityDetailComponentFactory>)factory
          entityDetail:(id<STEntityDetail>)entityDetail
              andFrame:(CGRect)frame;

- (id)initWithDelegate:(id<STViewDelegate>)delegate
            completion:(void(^)(STSynchronousWrapper*))completionBlock
          factoryBlock:(STViewFactoryBlock)factoryBlock
              andFrame:(CGRect)frame;

+ (STSynchronousWrapper*)wrapperForEntityDetail:(id<STEntityDetail>)anEntityDetail 
                                      withFrame:(CGRect)frame 
                                       andStyle:(NSString*)style
                                       delegate:(id<STViewDelegate>)delegate;

@end
