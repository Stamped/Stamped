//
//  MusicDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/10/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "MusicDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"

@interface MusicDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end


@implementation MusicDetailViewController

@synthesize imageView;
@synthesize affiliateLogoView;

- (void)dealloc {
  self.imageView = nil;
  self.affiliateLogoView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)showContents {
  if ([entityObject_.subcategory isEqualToString:@"artist"])
      self.descriptionLabel.text = entityObject_.subcategory;

  if ([entityObject_.subcategory isEqualToString:@"album"]
      || [entityObject_.subcategory isEqualToString:@"song"]) {
    if (!entityObject_.artist)
      self.descriptionLabel.text = entityObject_.subcategory;
    else
      self.descriptionLabel.text = [NSString stringWithFormat:@"by %@", entityObject_.artist];
  }

  if (entityObject_.image) {
    self.imageView.hidden = NO;
    self.imageView.image = [UIImage imageWithData:[NSData dataWithContentsOfURL:
                                                   [NSURL URLWithString:entityObject_.image]]];
  }
  
  [self setupMainActionsContainer];
  [self setupSectionViews];
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
  self.imageView = nil;
  self.affiliateLogoView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_itunes"];

  self.imageView.layer.shadowOffset  = CGSizeMake(0.0, 4.0);
  self.imageView.layer.shadowRadius  = 4.0;
  self.imageView.layer.shadowColor   = [UIColor blackColor].CGColor;
  self.imageView.layer.shadowOpacity = 0.33;
  
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
   [NSURL URLWithString:entityObject_.itunesShortURL]];
}



#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {
  if (entityObject_.itunesShortURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden  = NO;
    self.mainActionsView.hidden  = NO;
  }
  
  else self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
}

- (void)setupSectionViews {
  // Tracks
  if (entityObject_.songs) {
    NSArray* tracksArray = entityObject_.songs;
    
    [self addSectionWithName:@"Tracks" previewHeight:136.f];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Tracks"];
    section.collapsedFooterText = [NSString stringWithFormat:@"Show all %d tracks", tracksArray.count];
    section.expandedFooterText = @"Show less";
    section.footerLabel.text = section.collapsedFooterText;
    [section addNumberedListWithValues:tracksArray];
    section.arrowView.frame = CGRectOffset(section.arrowView.frame, 
                                           [section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 8.0, 0);
    self.mainContentView.hidden = NO;
  }

  // Details
  if (entityObject_.genre || entityObject_.releaseDate) {
    
    [self addSectionWithName:@"Details"];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Details"];
    
    if (entityObject_.genre)
      [section addPairedLabelWithName:@"Genres" value:entityObject_.genre forKey:@"genre"]; 
    if (entityObject_.releaseDate)
      [section addPairedLabelWithName:@"Release Date" value:entityObject_.releaseDate forKey:@"releaseDate"];

    self.mainContentView.hidden = NO;
  }
  
  if (entityObject_.desc) {
    [self addSectionWithName:@"iTunes Notes"];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"iTunes Notes"];
    [section addText:entityObject_.desc forKey:@"desc"];
    
    self.mainContentView.hidden = NO;
  }
  
  
  // Stamped by  
  NSSet* stamps = entityObject_.stamps;
  
  if (stamps && stamps.count > 0) {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO; 
  }
}

@end
