//
//  ActivityFollowTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 9/26/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ActivityFollowTableViewCell.h"

#import <CoreText/CoreText.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"

@implementation ActivityFollowTableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithReuseIdentifier:reuseIdentifier];
  if (self) {    
    badgeImageView_.image = [UIImage imageNamed:@"activity_follow_badge"];
  }
  return self;
}

- (NSAttributedString*)headerAttributedStringWithColor:(UIColor*)color {
  NSString* user = self.event.user.screenName;
  
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* full = [NSString stringWithFormat:@"%@ is now following you", user];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)color.CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName value:(id)font range:NSMakeRange(0, user.length)];
  CFRelease(font);
  CFRelease(style);
  return [string autorelease];
}
@end
