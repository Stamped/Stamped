//
//  STLoadingMoreTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLoadingMoreTableViewCell.h"

@interface STLoadingMoreTableViewCell ()
@property (nonatomic, readonly) UIActivityIndicatorView* spinner;
@end

@implementation STLoadingMoreTableViewCell

@synthesize spinner = spinner_;

+ (STLoadingMoreTableViewCell*)cell {
  return [[[STLoadingMoreTableViewCell alloc] init] autorelease];
}

- (id)init {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:nil];
  if (self) {
    self.selectionStyle = UITableViewCellSelectionStyleNone;
    spinner_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    [self.contentView addSubview:spinner_];
    [spinner_ startAnimating];
    [spinner_ release];
  }
  return self;
}

- (void)dealloc {
  spinner_ = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  spinner_.center = self.contentView.center;
}

@end
