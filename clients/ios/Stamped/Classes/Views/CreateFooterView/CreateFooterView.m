//
//  CreateFooterView.m
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import "CreateFooterView.h"
#import <CoreText/CoreText.h>
#import "STSimpleUserDetail.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STTwitter.h"
#import "STEvents.h"

@interface CreateFooterViewTextLayer : CATextLayer
@end
@implementation CreateFooterViewTextLayer

- (void)drawInContext:(CGContextRef)ctx {
    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 0.0f, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor);
    [super drawInContext:ctx];
}

@end

@interface CreateFooterView ()

@property (nonatomic, readonly, retain) UILabel* twitterText;

@end

@implementation CreateFooterView
@synthesize delegate;
@synthesize stampButton;
@synthesize twitterButton = _twitterButton;
@synthesize twitterText = _twitterText;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        [STEvents addObserver:self selector:@selector(twitterFailed:) event:EventTypeTwitterAuthFailed];
        
        self.backgroundColor = [UIColor clearColor];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor colorWithWhite:0.689f alpha:1.0f];
        label.font = [UIFont systemFontOfSize:12];
        label.backgroundColor = self.backgroundColor;
        [self addSubview:label];
        [label release];
        
        UIImage *image = [UIImage imageNamed:@"create_stamp_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button addTarget:self action:@selector(stamp:) forControlEvents:UIControlEventTouchUpInside];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin;
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:image.size.height] forState:UIControlStateNormal];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        [button setTitle:@"Stamp it!" forState:UIControlStateNormal];
        [button setTitle:@"Uploading..." forState:UIControlStateDisabled];
        button.contentEdgeInsets = UIEdgeInsetsMake(0.0f, 0.0f, 2.0f, 0.0f);
        [self addSubview:button];
        button.frame = CGRectMake((self.bounds.size.width-106.0f), self.bounds.size.height - (image.size.height+6.0f), 96.0f, image.size.height);
        self.stampButton = button;
        
        if ([STTwitter sharedInstance].canTweet) {
            image = [UIImage imageNamed:@"tweetbtn"];
            button = [UIButton buttonWithType:UIButtonTypeCustom];
            [button setImage:image forState:UIControlStateNormal];
            [button setImage:[UIImage imageNamed:@"tweetbtn_active"] forState:UIControlStateSelected];
            [button setImage:[UIImage imageNamed:@"tweetbtn_down"] forState:UIControlStateHighlighted];
            [button addTarget:self action:@selector(twitter:) forControlEvents:UIControlEventTouchUpInside];
            [self addSubview:button];
            button.frame = CGRectMake(10.0f, self.bounds.size.height - (image.size.height+10.0f), image.size.width, image.size.height);
            
            _twitterButton = [button retain];
            //
            //        image = [UIImage imageNamed:@"share_fb"];
            //        button = [UIButton buttonWithType:UIButtonTypeCustom];
            //        [button setImage:image forState:UIControlStateNormal];
            //        [button setImage:[UIImage imageNamed:@"share_fb_on"] forState:UIControlStateSelected];
            //        [button setImage:[UIImage imageNamed:@"share_fb_highlighted"] forState:UIControlStateHighlighted];
            //        [button addTarget:self action:@selector(facebook:) forControlEvents:UIControlEventTouchUpInside];
            //        [self addSubview:button];
            //        button.frame = CGRectMake(12.0f + image.size.width, self.bounds.size.height - (image.size.height+10.0f), image.size.width, image.size.height);
            //        
            //        
            
            _twitterText = [[Util viewWithText:@"" //Keep in case re-enabled
                                          font:[UIFont stampedFontWithSize:12]
                                         color:[UIColor stampedGrayColor]
                                          mode:UILineBreakModeTailTruncation
                                    andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)] retain];
            _twitterText.frame = CGRectMake(CGRectGetMaxX(button.frame) + 10, button.frame.origin.y, _twitterText.frame.size.width, button.frame.size.height);
            [self addSubview:_twitterText];
        }
        id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
        if ([user respondsToSelector:@selector(numStampsLeft)]) {
            
            NSInteger count = [[(STSimpleUserDetail*)user numStampsLeft] integerValue];
            NSString *title = [NSString stringWithFormat:@"You have %i stamp%@ left.", count, count==1 ? @"" : @"s"];
            
            UIColor *textColor = [UIColor colorWithRed:0.698f green:0.698f blue:0.698f alpha:1.0f];
            CTFontRef ctFont = CTFontCreateWithName([[UIScreen mainScreen] scale] == 2.0 ? (CFStringRef)@"HelveticaNeue" : (CFStringRef)@"Helvetica", 10, NULL);
            CTFontRef boldFont = CTFontCreateCopyWithSymbolicTraits(ctFont, 0.0, NULL, kCTFontBoldTrait, kCTFontBoldTrait);
            NSMutableDictionary *boldStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)boldFont, kCTFontAttributeName, (id)textColor.CGColor, kCTForegroundColorAttributeName, nil];
            
            NSMutableDictionary *defaultStyle = [[NSMutableDictionary alloc] initWithObjectsAndKeys:(NSString*)ctFont, kCTFontAttributeName, (id)textColor.CGColor, kCTForegroundColorAttributeName, nil];
            
            CFRelease(ctFont);
            CFRelease(boldFont);
            
            NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:title attributes:defaultStyle];
            [string setAttributes:boldStyle range:[string.string rangeOfString:[NSString stringWithFormat:@"%i", count]]];
            
            [defaultStyle release];
            [boldStyle release];
            
            CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString( (CFMutableAttributedStringRef) string); 
            CGFloat width = ceilf(CTFramesetterSuggestFrameSizeWithConstraints(framesetter, CFRangeMake(0, 0), NULL, CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX), NULL).width);
            CFRelease(framesetter);
            
            CreateFooterViewTextLayer *textLayer = [CreateFooterViewTextLayer layer];
            textLayer.contentsScale = [[UIScreen mainScreen] scale];
            textLayer.frame = CGRectMake(ceilf(self.bounds.size.width-(width+12.0f)), 10.0f, ceilf(width), 14);
            textLayer.string = string;
            [self.layer addSublayer:textLayer];
            [string release];
            
        }
        
    }
    return self;
}

- (void)dealloc {
    [_twitterButton release];
    [STEvents removeObserver:self];
    [_twitterText release];
    self.stampButton=nil;
    self.delegate=nil;
    [super dealloc];
}

- (CGFloat)boundingWidthForAttributedString:(NSAttributedString *)attributedString {
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString( (CFMutableAttributedStringRef) attributedString); 
    CGSize suggestedSize = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, CFRangeMake(0, 0), NULL, CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX), NULL);
    CFRelease(framesetter);
    return suggestedSize.width;
}

- (void)setUploading:(BOOL)uploading animated:(BOOL)animated {
    
    self.stampButton.enabled = !uploading;
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:animated];
    
    if (uploading) {
        
        [UIView animateWithDuration:0.3f animations:^{
            self.stampButton.alpha = 0.9f;
        }];
        
    } else {
        
        self.stampButton.alpha = 1.0f;
        CAKeyframeAnimation *scale = [CAKeyframeAnimation animationWithKeyPath:@"transform.scale"];
        scale.duration = 0.45f;
        scale.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
        scale.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.1f], [NSNumber numberWithFloat:.9f], [NSNumber numberWithFloat:1.f], nil];
        [self.stampButton.layer addAnimation:scale forKey:nil];
        
    }
    
    [UIView setAnimationsEnabled:_enabled];
    
    
}


#pragma mark - Actions

- (void)twitter:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createFooterView:twitterSelected:)]) {
        [self.delegate createFooterView:self twitterSelected:sender];
    }
    UIButton* button = sender;
    _twitterText.textColor = button.selected ? [UIColor stampedLinkColor] : [UIColor stampedGrayColor];
}

- (void)twitterFailed:(id)notImportant {
    self.twitterButton.selected = YES;
    [self twitter:self.twitterButton];
}

- (void)stamp:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createFooterView:stampIt:)]) {
        [self.delegate createFooterView:self stampIt:sender];
    }
    
}

@end
