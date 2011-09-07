//
//  UserImageView.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "UserImageView.h"

#import <QuartzCore/QuartzCore.h>

#import "UserImageDownloadManager.h"

@interface UserImageView ()
- (void)initialize;
- (void)imageChanged:(NSNotification*)notification;
@end

@implementation UserImageView

@synthesize imageURL = imageURL_;
@synthesize imageView = imageView_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self initialize];

  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self initialize];

  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [super dealloc];
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.layer.bounds].CGPath;
}

- (void)initialize {
  self.enabled = NO;
  CALayer* backgroundLayer = [[CALayer alloc] init];
  backgroundLayer.frame = self.bounds;
  backgroundLayer.backgroundColor = [UIColor whiteColor].CGColor;
  [self.layer addSublayer:backgroundLayer];
  [backgroundLayer release];
  CGFloat borderWidth = CGRectGetWidth(self.frame) > 35.0 ? 2.0 : 1.0;
  imageView_ = [[UIImageView alloc] initWithFrame:CGRectInset(self.bounds, borderWidth, borderWidth)];
  imageView_.image = [UIImage imageNamed:@"profile_placeholder"];
  [self addSubview:imageView_];
  [imageView_ release];
  CALayer* layer = self.layer;
  layer.contentsGravity = kCAGravityResizeAspect;
  layer.frame = self.frame;
  layer.shadowOpacity = 0.25;
  layer.shadowOffset = CGSizeMake(0, 0.5);
  layer.shadowRadius = 1.0;
  layer.shadowPath = [UIBezierPath bezierPathWithRect:self.bounds].CGPath;
  [[NSNotificationCenter defaultCenter] addObserver:self 
                                           selector:@selector(imageChanged:)
                                               name:kUserImageLoadedNotification
                                             object:nil];
}

- (void)setImageURL:(NSString*)imageURL {
  imageURL_ = [imageURL copy];
  if (imageURL_) {
    imageView_.image =
        [[UserImageDownloadManager sharedManager] profileImageAtURL:imageURL_];
  }
  [self setNeedsDisplay];
}

- (void)imageChanged:(NSNotification*)notification {
  NSString* url = notification.object;
  if ([imageURL_ isEqualToString:url]) {
    self.imageURL = url;
  }
}

@end
