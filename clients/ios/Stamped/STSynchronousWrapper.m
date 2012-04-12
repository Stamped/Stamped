//
//  STSynchronousWrapper.m
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSynchronousWrapper.h"
#import "STEntityDetailViewFactory.h"
#import "STWeakProxy.h"
#import "Util.h"

@interface STSynchronousWrapper()

- (void)handleCallback:(STViewCreator)creator;

@property (nonatomic, retain) UIActivityIndicatorView* loadingView;
@property (nonatomic, retain) STWeakProxy* proxy;
@property (nonatomic, copy) void(^completion)(STSynchronousWrapper*);

@end

@implementation STSynchronousWrapper

@synthesize loadingView = _loadingView;
@synthesize proxy = _proxy;
@synthesize completion = _completion;

- (id)initWithDelegate:(id<STViewDelegate>)delegate
      componentFactory:(id<STEntityDetailComponentFactory>)factory
          entityDetail:(id<STEntityDetail>)entityDetail
              andFrame:(CGRect)frame {
  return [self initWithDelegate:delegate frame:frame factoryBlock:^(STViewCreatorCallback callback) {
    NSOperation* operation = [factory createViewWithEntityDetail:entityDetail andCallbackBlock:callback];
    [Util runOperationAsynchronously:operation];
  } andCompletion:nil];
}

- (id)initWithDelegate:(id<STViewDelegate>)delegate
                 frame:(CGRect)frame
          factoryBlock:(STViewFactoryBlock)factoryBlock
         andCompletion:(void(^)(STSynchronousWrapper*))completionBlock {
  self = [super initWithDelegate:delegate andFrame:frame];
  if (self) {
    _proxy = [[STWeakProxy alloc] initWithValue:self];
    _loadingView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    _loadingView.frame = CGRectMake(0, 0, frame.size.width, frame.size.height);
    _completion = [completionBlock copy];
    [self addSubview:_loadingView];
    _loadingView.hidden = NO;
    [_loadingView startAnimating];
    STWeakProxy* weakproxy = _proxy;
    factoryBlock(^(STViewCreator creator) {
      STSynchronousWrapper* wrapper = weakproxy.value;
      if (wrapper) {
        [wrapper handleCallback:creator];
      }
    });
  }
  return self;
}

- (void)dealloc
{
  self.proxy.value = nil;
  [_proxy release];
  [_loadingView release];
  [_completion release];
  [super dealloc];
}


- (void)handleCallback:(STViewCreator)creator {
  UIView* child;
  if (creator) {
    child = creator(self);
  }
  CGFloat delta;
  void (^completion_block)(BOOL) = nil;
  if (child) {
    delta = child.frame.size.height - self.frame.size.height;
    completion_block = ^(BOOL finished) {
      [self.loadingView stopAnimating];
      [self.loadingView removeFromSuperview];
      CGRect frame = self.frame;
      frame.size.height = 0;
      self.frame = frame;
      [self appendChildView:child];
      if (self.completion) {
        self.completion(self);
      }
    };
  }
  else {
    delta = -self.frame.size.height;
  }
  CGFloat duration = .15;
  if ([self.delegate respondsToSelector:@selector(childView:shouldChangeHeightBy:overDuration:)]) {
    [self.delegate childView:self shouldChangeHeightBy:delta overDuration:duration];
  }
  else {
    [UIView animateWithDuration:duration animations:^{
      CGRect frame = self.frame;
      frame.size.height += delta;
      self.frame = frame;
    }];
  }
  if (child) {
    [UIView animateWithDuration:duration animations:^{
      CGRect frame = self.loadingView.frame;
      frame.size.height += delta;
      self.loadingView.frame = frame;
    } completion:completion_block];
  }
  else {
    [self.loadingView stopAnimating];
    [self.loadingView removeFromSuperview];
  }
}

+ (STSynchronousWrapper*)wrapperForEntityDetail:(id<STEntityDetail>)anEntityDetail 
                                      withFrame:(CGRect)frame 
                                       andStyle:(NSString*)style
                                       delegate:(id<STViewDelegate>)delegate {
  id<STEntityDetailComponentFactory> factory = [[[STEntityDetailViewFactory alloc] initWithStyle:style] autorelease];
  return [[[STSynchronousWrapper alloc] initWithDelegate:delegate componentFactory:factory entityDetail:anEntityDetail andFrame:frame] autorelease];
}

@end