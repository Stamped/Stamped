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
@property (nonatomic, readwrite, retain) UIView* failureView;

@end

@implementation STSynchronousWrapper

@synthesize loadingView = _loadingView;
@synthesize proxy = _proxy;
@synthesize completion = _completion;
@synthesize failureView = _failureView;

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
      _loadingView.frame = [Util centeredAndBounded:_loadingView.frame.size inFrame:[Util originRectWithRect:self.frame]];
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
  [_failureView release];
  [super dealloc];
}


- (void)handleCallback:(STViewCreator)creator {
  UIView* child = nil;
  if (creator) {
    child = creator(self);
  }
  if (!child) {
    child = self.failureView;
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
      frame.origin.y += delta/2;
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
  id<STEntityDetailComponentFactory> factory = [[[STEntityDetailViewFactory alloc] initWithContext:[STActionContext context]] autorelease];
  STSynchronousWrapper* wrapper = [[[STSynchronousWrapper alloc] initWithDelegate:delegate
                                                                 componentFactory:factory 
                                                                     entityDetail:anEntityDetail 
                                                                         andFrame:frame] autorelease];
  return wrapper;
}


+ (STSynchronousWrapper*)wrapperForStampDetail:(id<STEntityDetail>)anEntityDetail 
                                     withFrame:(CGRect)frame 
                                         stamp:(id<STStamp>)stamp
                                      delegate:(id<STViewDelegate>)delegate {
  STActionContext* context = [STActionContext context];
  context.stamp = stamp;
  id<STEntityDetailComponentFactory> factory = [[[STEntityDetailViewFactory alloc] initWithContext:context] autorelease];
  STSynchronousWrapper* wrapper = [[[STSynchronousWrapper alloc] initWithDelegate:delegate
                                                                 componentFactory:factory 
                                                                     entityDetail:anEntityDetail 
                                                                         andFrame:frame] autorelease];
  return wrapper;
}

@end
