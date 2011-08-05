//
//  UserImageView.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "UserImageView.h"

#import <QuartzCore/QuartzCore.h>

@interface UserImageView ()
- (void)initialize;
@end

@implementation UserImageView

@synthesize image = image_;

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
  self.image = nil;
  [super dealloc];
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  self.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.layer.bounds].CGPath;
}

- (void)initialize {
  CALayer* layer = self.layer;
  layer.contentsGravity = kCAGravityResizeAspect;
  layer.frame = self.frame;
  layer.borderColor = [UIColor whiteColor].CGColor;
  layer.borderWidth = CGRectGetWidth(self.frame) > 35.0 ? 2.0 : 1.0;
  layer.shadowOpacity = 0.5;
  layer.shadowOffset = CGSizeMake(0, 0.5);
  layer.shadowRadius = 1.0;
  layer.shadowPath = [UIBezierPath bezierPathWithRect:layer.bounds].CGPath;
}

- (void)setImage:(UIImage*)image {
  if (image != image_) {
    [image_ release];
    image_ = [image retain];
    self.layer.contents = (id)image.CGImage;
  }
}

@end
