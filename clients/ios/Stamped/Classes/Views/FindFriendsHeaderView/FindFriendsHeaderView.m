//
//  FindFriendsHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "FindFriendsHeaderView.h"
#import <CoreText/CoreText.h>

@implementation FindFriendsHeaderView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        CGFloat originY = 10.0f;
        CGFloat originX = 10.0f;
        CGFloat width = self.bounds.size.width-20.0f;
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        UIImage *image = [UIImage imageNamed:@"welcome_facebook_btn.png"];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:image.size.width - 6.0f topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(originX, originY, width, image.size.height);
        button.tag = (FindFriendsSelectionTypeFacebook+1)*100;
        [self addSubview:button];
        CATextLayer *textLayer = [self addTitle:@"Find friends from Facebook" toButton:button boldText:@"Facebook"];
        textLayer.alignmentMode = @"left";
        frame = textLayer.frame;
        frame.origin.x = 60.0f;
        frame.origin.y -= 1.0f;
        textLayer.frame = frame;
        
        originY = CGRectGetMaxY(button.frame) + 4.0f;
        
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        image = [UIImage imageNamed:@"welcome_twitter_btn.png"];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:image.size.width - 6.0f topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(originX, originY, width, image.size.height);
        button.tag = (FindFriendsSelectionTypeTwitter+1)*100;
        [self addSubview:button];
        textLayer = [self addTitle:@"Find friends from Twitter" toButton:button boldText:@"Twitter"];
        textLayer.alignmentMode = @"left";
        frame = textLayer.frame;
        frame.origin.x = 60.0f;
        frame.origin.y -= 1.0f;
        textLayer.frame = frame;
        
        originY = CGRectGetMaxY(button.frame) + 4.0f;

        button = [UIButton buttonWithType:UIButtonTypeCustom];
        image = [UIImage imageNamed:@"welcome_email_brown_btn.png"];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:image.size.width - 6.0f topCapHeight:0] forState:UIControlStateNormal];
        button.frame = CGRectMake(originX, originY, width, image.size.height);
        button.tag = (FindFriendsSelectionTypeContacts+1)*100;
        [self addSubview:button];
        textLayer = [self addTitle:@"Find friends from Contacts" toButton:button boldText:@"Contacts"];
        textLayer.alignmentMode = @"left";
        frame = textLayer.frame;
        frame.origin.x = 60.0f;
        frame.origin.y -= 1.0f;
        textLayer.frame = frame;

    }
    return self;
}

- (CATextLayer*)addTitle:(NSString*)title toButton:(UIButton*)button boldText:(NSString*)boldText {
    
    CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"Helvetica Neue" : (CFStringRef)@"Helvetica", 12, NULL);
    CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
    NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, kCTForegroundColorAttributeName, nil];
    
    CFRelease(ctFont);
    CFRelease(boldFont);
    
    NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
    if (boldText) {
        [string setAttributes:boldStyle range:[string.string rangeOfString:boldText]];
    }
    [boldStyle release];
    [defaultStyle release];
    
    CATextLayer *layer = [CATextLayer layer];
    layer.contentsScale = [[UIScreen mainScreen] scale];
    layer.frame = CGRectMake(0.0f, floorf((button.bounds.size.height - 14)/2), 180.0f, 14);
    layer.backgroundColor = [UIColor clearColor].CGColor;
    layer.alignmentMode = @"center";
    layer.string = string;
    [string release];
    [button.layer addSublayer:layer];
    return layer;
    
    
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {

    if ([(id)delegate respondsToSelector:@selector(findFriendsHeaderView:selectedType:)]) {
        [self.delegate findFriendsHeaderView:self selectedType:([sender tag]/100)-1];
    }
    
}


@end
