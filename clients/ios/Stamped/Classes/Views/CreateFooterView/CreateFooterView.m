//
//  CreateFooterView.m
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import "CreateFooterView.h"

@implementation CreateFooterView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor colorWithWhite:0.689f alpha:1.0f];
        label.font = [UIFont systemFontOfSize:10];
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
        [self addSubview:button];
        button.frame = CGRectMake((self.bounds.size.width-106.0f), self.bounds.size.height - (image.size.height+10.0f), 96.0f, image.size.height);
        
        image = [UIImage imageNamed:@"share_twitter"];
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button setImage:image forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"share_twitter_on"] forState:UIControlStateSelected];
        [button setImage:[UIImage imageNamed:@"share_twitter_highlighted"] forState:UIControlStateHighlighted];
        [button addTarget:self action:@selector(twitter:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        button.frame = CGRectMake(10.0f, self.bounds.size.height - (image.size.height+10.0f), image.size.width, image.size.height);

        image = [UIImage imageNamed:@"share_fb"];
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button setImage:image forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"share_fb_on"] forState:UIControlStateSelected];
        [button setImage:[UIImage imageNamed:@"share_fb_highlighted"] forState:UIControlStateHighlighted];
        [button addTarget:self action:@selector(facebook:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        button.frame = CGRectMake(12.0f + image.size.width, self.bounds.size.height - (image.size.height+10.0f), image.size.width, image.size.height);
        
    
    }
    return self;
}


#pragma mark - Actions

- (void)twitter:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createFooterView:twitterSelected:)]) {
        [self.delegate createFooterView:self twitterSelected:sender];
    }
    
}

- (void)facebook:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createFooterView:facebookSelected:)]) {
        [self.delegate createFooterView:self facebookSelected:sender];
    }
}

- (void)stamp:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createFooterView:stampIt:)]) {
        [self.delegate createFooterView:self stampIt:sender];
    }
    
}

@end
