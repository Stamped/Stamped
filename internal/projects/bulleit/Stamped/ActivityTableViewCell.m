//
//  ActivityTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityTableViewCell.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"

@implementation ActivityTableViewCell

@synthesize event = event_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;

    userImageView_ = [[UserImageView alloc] initWithFrame:CGRectZero];
    [self.contentView addSubview:userImageView_];
    [userImageView_ release];
    
    headerTextLayer_ = [[CATextLayer alloc] init];
    headerTextLayer_.truncationMode = kCATruncationEnd;
    headerTextLayer_.contentsScale = [[UIScreen mainScreen] scale];
    headerTextLayer_.fontSize = 12.0;
    headerTextLayer_.foregroundColor = [UIColor stampedGrayColor].CGColor;
    headerTextLayer_.frame = CGRectMake(70, 13, 210, 16);
    headerTextLayer_.actions = [NSDictionary dictionaryWithObject:[NSNull null]
                                                           forKey:@"contents"];
    [self.contentView.layer addSublayer:headerTextLayer_];
    [headerTextLayer_ release];

    UIImage* disclosureImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureArrowImageView_ = [[UIImageView alloc] initWithFrame:CGRectZero];
    disclosureArrowImageView_.contentMode = UIViewContentModeCenter;
    disclosureArrowImageView_.image = disclosureImage;
    disclosureArrowImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureImage];
    [self.contentView addSubview:disclosureArrowImageView_];
    [disclosureArrowImageView_ release];
  }
  return self;
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  disclosureArrowImageView_.frame =
      CGRectMake(290,
                 (CGRectGetHeight(self.contentView.frame) / 2) -
                     (CGRectGetHeight(disclosureArrowImageView_.frame) / 2),
                 8, 11);
}

- (void)setEvent:(Event*)event {
  if (event == event_)
    return;
  
  [event_ release];
  event_ = [event retain];
}

- (void)dealloc {
  self.event = nil;
  [super dealloc];
}

- (void)invertColors:(BOOL)inverted {
  UIColor* color = inverted ? [UIColor whiteColor] : [UIColor stampedGrayColor];
  headerTextLayer_.string = [self headerAttributedStringWithColor:color];
  [self setNeedsDisplayInRect:headerTextLayer_.frame];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [self invertColors:selected];
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
  [super setHighlighted:highlighted animated:animated];
  [self invertColors:highlighted];
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  // Stub. Should be implemented by subclasses.
  return nil;
}

@end
