//
//  SearchEntitiesAutoSuggestCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 11/2/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "SearchEntitiesAutoSuggestCell.h"

#import <QuartzCore/QuartzCore.h>

#import "UIColor+Stamped.h"

@implementation SearchEntitiesAutoSuggestCell

@synthesize textLabel = textLabel_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [self initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
  if (self) {
    self.contentView.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
    textLabel_ = [[UILabel alloc] initWithFrame:CGRectMake(36, 0, 264, 47)];
    textLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:16];
    textLabel_.backgroundColor = [UIColor colorWithWhite:0.95 alpha:1.0];
    textLabel_.textColor = [UIColor stampedBlackColor];
    textLabel_.highlightedTextColor = [UIColor whiteColor];
    [self.contentView addSubview:textLabel_];
    [textLabel_ release];
  }
  return self;
}

- (void)dealloc {
  textLabel_ = nil;
  [super dealloc];
}

@end
