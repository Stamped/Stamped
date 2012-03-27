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

@interface STSynchronousWrapper()

- (void)handleCallback:(STViewCreator)creator;

@property (nonatomic, retain) UIActivityIndicatorView* loadingView;
@property (nonatomic, retain) NSOperationQueue* queue;
@property (nonatomic, retain) STWeakProxy* proxy;

@end

@implementation STSynchronousWrapper

@synthesize loadingView = _loadingView;
@synthesize queue = _queue;
@synthesize proxy = _proxy;

- (id)initWithDelegate:(id<STViewDelegate>)delegate
      componentFactory:(id<STEntityDetailComponentFactory>)factory
          entityDetail:(id<STEntityDetail>)entityDetail
              andFrame:(CGRect)frame {
  self = [super initWithDelegate:delegate andFrame:frame];
  if (self) {
    _proxy = [[STWeakProxy alloc] initWithValue:self];
    _queue = [[NSOperationQueue alloc] init];
    _loadingView = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    _loadingView.frame = CGRectMake(0, 0, frame.size.width, frame.size.height);
    [self addSubview:_loadingView];
    _loadingView.hidden = NO;
    [_loadingView startAnimating];
    STWeakProxy* weakproxy = _proxy;
    NSOperation* operation = [factory createViewWithEntityDetail:entityDetail andCallbackBlock:^(STViewCreator creator) {
      STSynchronousWrapper* wrapper = weakproxy.value;
      if (wrapper) {
        [wrapper handleCallback:creator];
      }
    }];
    [_queue addOperation:operation];
  }
  return self;
}

- (void)dealloc
{
  self.proxy.value = nil;
  [_proxy release];
  [_queue release];
  [_loadingView release];
  [super dealloc];
}


- (void)handleCallback:(STViewCreator)creator {
  UIView* child = creator(self);
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
    };
  }
  else {
    delta = -self.frame.size.height;
  }
  CGFloat duration = .25;
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
