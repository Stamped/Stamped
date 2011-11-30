//
//  MusicDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/10/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "MusicDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "DetailedEntity.h"
#import "Entity.h"

@interface MusicDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end


@implementation MusicDetailViewController

@synthesize affiliateLogoView = affiliateLogoView_;

- (void)dealloc {
  self.affiliateLogoView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)showContents {
  if ([detailedEntity_.subcategory isEqualToString:@"artist"])
      self.descriptionLabel.text = detailedEntity_.subcategory;

  if ([detailedEntity_.subcategory isEqualToString:@"album"]
      || [detailedEntity_.subcategory isEqualToString:@"song"]) {
    if (!detailedEntity_.artist)
      self.descriptionLabel.text = detailedEntity_.subcategory;
    else
      self.descriptionLabel.text = [NSString stringWithFormat:@"by %@", detailedEntity_.artist];
  }

  if (detailedEntity_.image && ![detailedEntity_.image isEqualToString:@""]) {
    self.imageView.imageURL = detailedEntity_.image;
    self.imageView.delegate = self;
    UITapGestureRecognizer* gr = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(imageViewTapped)];
    [self.imageView addGestureRecognizer:gr];
    [gr release];
  } else {
    [self setupMainActionsContainer];
    [self setupSectionViews];
  }
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width, 480);
  self.mainActionButton.hidden = YES;
  self.mainActionLabel.hidden  = YES;
  self.mainActionsView.hidden  = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.affiliateLogoView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_itunes"];  
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:
   [NSURL URLWithString:detailedEntity_.itunesShortURL]];
}

#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {
  if (detailedEntity_.itunesShortURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden = NO;
    self.mainActionsView.hidden = NO;
  } else {
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
  }
}

- (void)setupSectionViews {
  // Tracks
  if (detailedEntity_.songs && ((NSArray*)detailedEntity_.songs).count > 0) {
    if ([detailedEntity_.subcategory isEqualToString:@"artist"]) {
      NSArray* tracksArray = detailedEntity_.songs;
      
      [self addSectionWithName:@"Top Songs" previewHeight:136.f];
      CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Top Songs"];
      section.collapsedFooterText = [NSString stringWithFormat:@"Show all %d songs", tracksArray.count];
      section.expandedFooterText = @"Show less";
      section.footerLabel.text = section.collapsedFooterText;
      [section addNumberedListWithValues:tracksArray];
      CGRect frame = section.arrowView.frame;
      frame.origin = CGPointMake([section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 15.0, section.arrowView.frame.origin.y);
      section.arrowView.frame = frame;
      self.mainContentView.hidden = NO;
    } else {
      NSArray* tracksArray = detailedEntity_.songs;
      
      [self addSectionWithName:@"Tracks" previewHeight:136.f];
      CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Tracks"];
      section.collapsedFooterText = [NSString stringWithFormat:@"Show all %d tracks", tracksArray.count];
      section.expandedFooterText = @"Show less";
      section.footerLabel.text = section.collapsedFooterText;
      [section addNumberedListWithValues:tracksArray];
      CGRect frame = section.arrowView.frame;
      frame.origin = CGPointMake([section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 15.0, section.arrowView.frame.origin.y);
      section.arrowView.frame = frame;
      self.mainContentView.hidden = NO;
    }
  }
  
  // Albums
  if (detailedEntity_.albums && ((NSArray*)detailedEntity_.albums).count > 0) {
    NSArray* albumsArray = detailedEntity_.albums;
    if ([sectionsDict_ objectForKey:@"Top Songs"]) {
      [self addSectionWithName:@"Albums"];
      CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Albums"];
      [section addNumberedListWithValues:albumsArray];
      section.numLabel.hidden = NO;
      section.numLabel.text = [NSString stringWithFormat:@"(%d)", albumsArray.count];
      section.numLabel.frame = CGRectOffset(section.numLabel.frame, -42.0, 0.0);
      self.mainContentView.hidden = NO;
    } else {
      [self addSectionWithName:@"Albums" previewHeight:136.f];
      CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Albums"];
      section.collapsedFooterText = [NSString stringWithFormat:@"Show all %d albums", albumsArray.count];
      section.expandedFooterText = @"Show less";
      section.footerLabel.text = section.collapsedFooterText;
      [section addNumberedListWithValues:albumsArray];
      CGRect frame = section.arrowView.frame;
      frame.origin = CGPointMake([section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 15.0, section.arrowView.frame.origin.y);
      section.arrowView.frame = frame;
      self.mainContentView.hidden = NO;
   }

    // Details
    if (detailedEntity_.genre || detailedEntity_.releaseDate) {
      
      CollapsibleViewController* section = [self makeSectionWithName:@"Details"];
        
      if (detailedEntity_.genre && ![detailedEntity_.genre isEqualToString:@""])
        [section addPairedLabelWithName:@"Genres" value:detailedEntity_.genre forKey:@"genre"]; 
      if (detailedEntity_.releaseDate && ![detailedEntity_.releaseDate isEqualToString:@""])
        [section addPairedLabelWithName:@"Release Date" value:detailedEntity_.releaseDate forKey:@"releaseDate"];

      if (section.contentDict.objectEnumerator.allObjects.count > 0) {
        [self addSection:section];
        self.mainContentView.hidden = NO;
      }
    }
    
    if (detailedEntity_.desc && ![detailedEntity_.desc isEqualToString:@""]) {
      [self addSectionWithName:@"iTunes Notes"];
      CollapsibleViewController* section = [sectionsDict_ objectForKey:@"iTunes Notes"];
      [section addText:detailedEntity_.desc forKey:@"desc"];
      
      if (section.contentDict.objectEnumerator.allObjects.count > 0)
        self.mainContentView.hidden = NO;
    }
    
    
    // Stamped by  
    NSSet* stamps = entityObject_.stamps;
    
    if (stamps && stamps.count > 0) {
      [self addSectionStampedBy];
      self.mainContentView.hidden = NO; 
    }
  }
}

#pragma mark - STImageViewDelegate methods.

- (void)STImageView:(STImageView*)imageView didLoadImage:(UIImage*)image {
  self.imageView.contentMode = UIViewContentModeScaleAspectFit;
  self.imageView.layer.backgroundColor = [UIColor clearColor].CGColor;
  self.imageView.hidden = NO;
  self.imageView.layer.shadowOffset = CGSizeMake(0.0, 4.0);
  self.imageView.layer.shadowRadius = 4.0;
  self.imageView.layer.shadowColor = [UIColor blackColor].CGColor;
  self.imageView.layer.shadowOpacity = 0.33;
  CGRect imageFrame = [Util frameForImage:self.imageView.image inImageViewAspectFit:self.imageView];
  self.imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageFrame].CGPath;
  [self setupMainActionsContainer];
  [self setupSectionViews];
}

@end
