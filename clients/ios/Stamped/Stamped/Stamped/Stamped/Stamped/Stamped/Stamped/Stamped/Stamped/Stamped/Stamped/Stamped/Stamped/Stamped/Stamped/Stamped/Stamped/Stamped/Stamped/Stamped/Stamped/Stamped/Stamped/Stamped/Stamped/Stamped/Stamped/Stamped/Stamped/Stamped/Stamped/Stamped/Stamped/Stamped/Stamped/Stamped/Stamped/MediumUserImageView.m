//
//  MediumUserImageView.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/6/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "MediumUserImageView.h"
#import "UserImageDownloadManager.h"

#import <QuartzCore/QuartzCore.h>

@interface MediumUserImageView ()
- (void)mediumImageChanged:(NSNotification*)notification;
@end

@implementation MediumUserImageView

@synthesize imageURL = imageURL_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:CGRectInset(frame, -2, -2)];
  if (self) {
    self.layer.shadowPath =
        [UIBezierPath bezierPathWithRect:CGRectInset(self.bounds, 2, 2)].CGPath;
    self.layer.shadowOffset = CGSizeMake(0, 1);
    self.layer.shadowOpacity = 0.2;
    self.layer.shadowRadius = 1.33;
    [[NSNotificationCenter defaultCenter] addObserver:self 
                                             selector:@selector(mediumImageChanged:)
                                                 name:@"kMediumUserImageLoadedNotification"
                                               object:nil];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.imageURL = nil;
  [super dealloc];
}

- (void)setImageURL:(NSString*)imageURL {
  if (![imageURL isEqualToString:imageURL_]) {
    [imageURL_ release];
    imageURL_ = [imageURL copy];
  }

  if (imageURL_)
    self.image = [[UserImageDownloadManager sharedManager] mediumProfileImageAtURL:imageURL_];

  [self setNeedsDisplay];
}

- (void)mediumImageChanged:(NSNotification*)notification {
  NSString* url = notification.object;
  if ([imageURL_ isEqualToString:url]) {
    self.imageURL = url;
  }
}

@end
