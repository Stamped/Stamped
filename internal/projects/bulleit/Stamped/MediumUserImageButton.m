//
//  MediumUserImageButton.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/8/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "MediumUserImageButton.h"

#import <QuartzCore/QuartzCore.h>

#import "UserImageDownloadManager.h"

@implementation MediumUserImageButton

@synthesize imageURL = imageURL_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [[NSNotificationCenter defaultCenter] addObserver:self 
                                             selector:@selector(mediumImageChanged:)
                                                 name:kMediumUserImageLoadedNotification
                                               object:nil];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [super dealloc];
}

- (void)setImageURL:(NSString*)imageURL {
  if (imageURL != imageURL_) {
    [imageURL_ release];
    imageURL_ = [imageURL copy];
    if (imageURL_) {
      UIImage* img = [[UserImageDownloadManager sharedManager] mediumProfileImageAtURL:imageURL_];
      [self setImage:img forState:UIControlStateNormal];
    }
    [self setNeedsDisplay];
  }
}

- (void)mediumImageChanged:(NSNotification*)notification {
  NSString* url = notification.object;
  if ([imageURL_ isEqualToString:url]) {
    self.imageURL = url;
  }
}

@end
